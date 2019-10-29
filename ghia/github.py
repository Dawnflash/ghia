import click
import requests


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
