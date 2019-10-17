#! /usr/bin/env python
"""
MI-PYT assignment by Adam Zahumensky <zahumada@fit.cvut.cz>

Running the app in Flask mode:
$ GHIA_CONFIG=<path_a, path_b, ...> FLASK_APP=ghia.py flask run
Use GHIA_DRYRUN env variable to set dry run
Set GHIA_STRATEGY to set|change to switch strategy (default: append)
"""

import configparser
import requests
import click
import re
import os
import flask
import hashlib
import hmac


# Flaskery!
app_hook_issues_action_wl = ['opened', 'edited', 'transferred', 'reopened',
                             'assigned', 'unassigned', 'labeled', 'unlabeled']
app = flask.Flask(__name__)

# The default web entry point
@app.route('/', methods=['GET', 'POST'])
def index():
    config = app.config['ghia']
    login = get_gh_login(config['github']['token'])

    if flask.request.method == 'GET':
        return flask.render_template('index.html', config=config, login=login)

    # Validate request
    if not webapp_gh_validate():
        flask.abort(403)

    # Respond to ping and issue events
    event = flask.request.headers.get('X-GitHub-Event')
    if event == 'ping':
        return '', 200

    if event == 'issues':
        return webapp_gh_issue_handler()

    flask.abort(404)


def webapp_gh_issue_handler():
    payload = flask.request.json
    # Only act on specific actions
    if payload['action'] not in app_hook_issues_action_wl:
        return '', 200

    issue = payload['issue']
    if not process_issue(issue, app.config['ghia']):
        flask.abort(400, description='Received issue cannot be processed')
    return '', 200


# Validate github webhook if applicable
def webapp_gh_validate():
    conf = app.config['ghia']
    # If secret is not set, do not authenticate
    if 'secret' not in conf['github']:
        return True

    secret = conf['github']['secret']
    sign_hdr = flask.request.headers.get('X-Hub-Signature')

    # Signature is mandatory
    if not sign_hdr:
        return False

    algo, sign = sign_hdr.split('=')
    dg = hmac.new(secret.encode('utf8'), flask.request.data, algo)
    return hmac.compare_digest(dg.hexdigest(), sign)


# Initialize the Flask application
def webapp_init():
    # Fetch configuration
    dry_run = 'GHIA_DRYRUN' in os.environ
    env_strategy = os.environ.get('GHIA_STRATEGY')
    strategy = env_strategy if env_strategy in ['set', 'change'] else 'append'
    env_conf = os.environ.get('GHIA_CONFIG')

    config = webapp_conf_fetch(env_conf)
    if not config:
        click.echo("Bad config", err=True)
        exit(10)

    app.config['ghia'] = config
    app.config['ghia']['strategy'] = strategy
    app.config['ghia']['dry_run'] = dry_run


def webapp_conf_fetch(paths):
    if paths is None:
        return None

    config = configparser.ConfigParser()
    config.optionxform = str
    try:
        config.read(paths.split(':'))
        return {**load_config_auth(config), **load_config_rules(config)}
    except Exception:
        return None


# ------------------------------- APP LOGIC -----------------------------------

# get authenticated user
def get_gh_login(token):
    url = 'https://api.github.com/user'
    r = requests.get(url, headers={'Authorization': f"token {token}"})

    if r.status_code != 200:
        click.echo("Unable to fetch user", err=True)
        exit(10)

    return r.json()['login']


# checks if any user pattern matches the issue
def check_match(issue, user, patterns):
    for item, rgx in patterns:
        if item == 'title' or item == 'any':
            if rgx.search(issue['title']):
                return True
        if item == 'text' or item == 'any':
            if rgx.search(issue['body']):
                return True
        if item == 'label' or item == 'any':
            for label in issue['labels']:
                if rgx.search(label['name']):
                    return True
    return False


def print_issue_update_error(issue):
    click.echo("   {}: Could not update issue {}".format(
            click.style('ERROR', bold=True, fg='red'),
            f"{issue['repository_url'].split('/repos/')[1]}#{issue['number']}"
        ), err=True)


def add_fallback_label(issue, config, verbose):
    label = config['fallback']['label']
    # check if fallback label already exists
    labels = [l['name'] for l in issue['labels']]
    has_label = label in labels

    if verbose:
        click.echo("   {}: {} label \"{}\"".format(
            click.style('FALLBACK', bold=True, fg='yellow'),
            'already has' if has_label else 'added',
            label
        ))

    if has_label or config['dry_run']:
        return True

    # publish changes to GitHub
    labels.append(label)
    token = config['github']['token']
    r = requests.patch(issue['url'],
                       json={'labels': labels},
                       headers={'Authorization': f"token {token}"})

    if r.status_code != 200:
        if verbose:
            print_issue_update_error(issue)
        return False
    return True


# publishes changes in assignees to GitHub
def reassign(token, old, new, issue, verbose):
    r = requests.patch(issue['url'],
                       json={'assignees': list(new)},
                       headers={'Authorization': f"token {token}"})

    if r.status_code != 200:
        if verbose:
            print_issue_update_error(issue)
            print_assign_diff(old, old)
        return False
    if verbose:
        print_assign_diff(old, new)
    return True


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


def process_issue(issue, config, verbose=False):
    if issue['state'] == 'closed':
        return True

    token = config['github']['token']
    old_assignees = set([usr['login'] for usr in issue['assignees']])

    # set strategy only assigns people to non-assigned issues
    if config['strategy'] == 'set' and len(old_assignees) > 0:
        if verbose:
            print_assign_diff(old_assignees, old_assignees)
        return True

    # append strategy keeps old assignees, others do not
    new_assignees = old_assignees.copy() if config['strategy'] == 'append' else set()

    for user in config['patterns']:
        patterns = config['patterns'][user]
        if check_match(issue, user, patterns):
            new_assignees.add(user)

    ret = True
    # use fallback label if it's set and the issue is empty
    if 'fallback' in config:
        if len(new_assignees) == 0:
            ret &= add_fallback_label(issue, config, verbose)

    # only send patch requests if necessary
    if not config['dry_run'] and new_assignees != old_assignees:
        return ret & reassign(token, old_assignees, new_assignees, issue, verbose)

    if verbose:
        print_assign_diff(old_assignees, new_assignees)
    return ret


def load_config(config_file):
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read_file(config_file)
    return config


def load_config_auth(config_parser):
    config = {'github': {'token': config_parser['github']['token']}}
    if config_parser.has_option('github', 'secret'):
        config['github']['secret'] = config_parser['github']['secret']
    return config


def load_config_rules(config_parser):
    config = {'patterns': {}}
    for user in config_parser['patterns']:
        config['patterns'][user] = []
        for line in config_parser['patterns'][user].splitlines():
            toks = line.split(':', 1)
            if len(toks) != 2:
                continue
            config['patterns'][user].append((toks[0], re.compile(toks[1], re.IGNORECASE)))

    if config_parser.has_option('fallback', 'label'):
        config['fallback'] = {'label': config_parser['fallback']['label']}
    return config


def click_validate_config_auth(ctx, param, value):
    try:
        return load_config_auth(load_config(value))
    except (Exception):
        raise click.BadParameter('incorrect configuration format')


def click_validate_config_rules(ctx, param, value):
    try:
        return load_config_rules(load_config(value))
    except (Exception):
        raise click.BadParameter('incorrect configuration format')


def click_validate_reposlug(ctx, param, value):
    rgx = '^[^/ ]+/[^/ ]+$'  # name/repo
    if not re.search(rgx, value):
        raise click.BadParameter('not in owner/repository format')
    return value


@click.command()
@click.option('-s', '--strategy', help='How to handle assignment collisions.',
              type=click.Choice(['append', 'set', 'change']),
              default='append', show_default=True)
@click.option('-d', '--dry-run', help='Run without making any changes.', is_flag=True)
@click.option('-a', '--config-auth', help='File with authorization configuration.',
              required=True, type=click.File('r'), callback=click_validate_config_auth)
@click.option('-r', '--config-rules', help='File with assignment rules configuration.',
              required=True, type=click.File('r'), callback=click_validate_config_rules)
@click.argument('reposlug', callback=click_validate_reposlug)
def main(strategy, dry_run, config_auth, config_rules, reposlug):
    """CLI tool for automatic issue assigning of GitHub issues"""

    config = {**config_auth, **config_rules}
    config['strategy'] = strategy
    config['dry_run'] = dry_run

    token = config['github']['token']
    issues = gather_issues(reposlug, token)

    for issue in issues:
        if issue['state'] == 'closed':
            continue
        click.echo("-> {} ({})".format(
            click.style(f"{reposlug}#{issue['number']}", bold=True),
            issue['html_url']
        ))
        process_issue(issue, config, verbose=True)

# Main entrypoint
if __name__ == '__main__':
    main()
else:
    webapp_init()
