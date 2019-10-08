#! /usr/bin/env python
"""
MI-PYT assignment by Adam Zahumensky <zahumada@fit.cvut.cz>
"""

import configparser
import requests
import click
import re


# checks if any user pattern matches the issue
def check_match(issue, user, patterns):
    for line in patterns.splitlines():
        toks = line.split(':', 1)
        if len(toks) != 2:
            continue
        item, rgx = toks
        if item == 'title' or item == 'any':
            if re.search(rgx, issue['title'], re.IGNORECASE):
                return True
        if item == 'text' or item == 'any':
            if re.search(rgx, issue['body'], re.IGNORECASE):
                return True
        if item == 'label' or item == 'any':
            for label in issue['labels']:
                if re.search(rgx, label['name'], re.IGNORECASE):
                    return True
    return False


def print_issue_update_error(issue):
    click.echo("   {}: Could not update issue {}".format(
            click.style('ERROR', bold=True, fg='red'),
            f"{issue['repository_url'].split('/repos/')[1]}#{issue['number']}"
        ), err=True)


def add_fallback_label(issue, token, label, dry_run):
    # check if fallback label already exists
    labels = [l['name'] for l in issue['labels']]
    has_label = label in labels

    click.echo("   {}: {} label \"{}\"".format(
        click.style('FALLBACK', bold=True, fg='yellow'),
        'already has' if has_label else 'added',
        label
    ))

    if has_label or dry_run:
        return

    # publish changes to GitHub
    labels.append(label)
    r = requests.patch(issue['url'],
                       json={'labels': labels},
                       headers={'Authorization': f"token {token}"})

    if r.status_code != 200:
        print_issue_update_error(issue)


# publishes changes in assignees to GitHub
def reassign(token, old, new, issue):
    r = requests.patch(issue['url'],
                       json={'assignees': list(new)},
                       headers={'Authorization': f"token {token}"})

    if r.status_code != 200:
        print_issue_update_error(issue)
        # print only remaining users as nothing is going to change
        print_assign_diff(old, old)
    else:
        # print the changes
        print_assign_diff(old, new)


def print_assign_diff(old, new):
    # outputs are meant to be sorted alphabetically, case-insensitive
    for user in sorted(new.union(old), key=str.casefold):
        if user not in new:
            # deletion
            click.echo(f"   {click.style('-', bold=True, fg='red')} {user}")
        elif user not in old:
            # addition
            click.echo(f"   {click.style('+', bold=True, fg='green')} {user}")
        else:
            # nothing
            click.echo(f"   {click.style('=', bold=True, fg='blue')} {user}")


# gathers issues from the API
def gather_issues(reposlug, token):
    user, repo = reposlug.split('/')
    url = f"https://api.github.com/repos/{user}/{repo}/issues"
    issues = []

    while True:
        # request issues
        r = requests.get(url, headers={'Authorization': f"token {token}"})

        if r.status_code != 200:
            click.echo("{}: Could not list issues for repository {}".format(
                click.style('ERROR', bold=True, fg='red'),
                reposlug
            ), err=True)
            exit(10)

        issues += r.json()
        # stop paginating once we reach the end
        if 'next' not in r.links:
            return issues

        url = r.links['next']['url']


def validate_reposlug(ctx, param, value):
    rgx = '^[^/ ]+/[^/ ]+$'  # name/repo
    if not re.search(rgx, value):
        raise click.BadParameter('not in owner/repository format')
    return value


def validate_config(value, check_fn):
    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read_file(value)
        if not check_fn(config):
            raise configparser.Error()
        return config
    except configparser.Error:
        raise click.BadParameter('incorrect configuration format')


def validate_config_auth(ctx, param, value):
    return validate_config(value, lambda c: c.has_option('github', 'token'))


def validate_config_rules(ctx, param, value):
    return validate_config(value, lambda c: c.has_section('patterns'))


@click.command()
@click.option('-s', '--strategy', help='How to handle assignment collisions.',
              type=click.Choice(['append', 'set', 'change']),
              default='append', show_default=True)
@click.option('-d', '--dry-run', help='Run without making any changes.', is_flag=True)
@click.option('-a', '--config-auth', help='File with authorization configuration.',
              required=True, type=click.File('r'), callback=validate_config_auth)
@click.option('-r', '--config-rules', help='File with assignment rules configuration.',
              required=True, type=click.File('r'), callback=validate_config_rules)
@click.argument('reposlug', callback=validate_reposlug)
def main(strategy, dry_run, config_auth, config_rules, reposlug):
    """CLI tool for automatic issue assigning of GitHub issues"""

    token = config_auth['github']['token']
    issues = gather_issues(reposlug, token)

    for issue in issues:
        # skip closed issues
        if issue['state'] == 'closed':
            continue

        # print the info line
        click.echo("-> {} ({})".format(
            click.style(f"{reposlug}#{issue['number']}", bold=True),
            issue['html_url']
        ))

        old_assignees = set([usr['login'] for usr in issue['assignees']])

        # set strategy only assigns people to non-assigned issues
        if strategy == 'set' and len(old_assignees) > 0:
            print_assign_diff(old_assignees, old_assignees)
            continue

        # append strategy keeps old assignees, others do not
        new_assignees = old_assignees.copy() if strategy == 'append' else set()

        for user in config_rules['patterns']:
            patterns = config_rules['patterns'][user]
            if check_match(issue, user, patterns):
                new_assignees.add(user)

        # use fallback label if it's set and the issue is empty
        if config_rules.has_option('fallback', 'label'):
            if len(old_assignees) == 0 and len(new_assignees) == 0:
                add_fallback_label(issue, token, config_rules['fallback']['label'], dry_run)

        # only send patch requests if necessary
        if not dry_run and new_assignees != old_assignees:
            reassign(token, old_assignees, new_assignees, issue)
        else:
            print_assign_diff(old_assignees, new_assignees)

if __name__ == '__main__':
    main()
