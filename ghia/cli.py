
"""Logic of the CLI batch interface
"""

import requests
import click
import re
from .helpers import load_config, load_config_auth, load_config_rules
from .github import gather_issues, process_issue


def click_validate_config_auth(ctx, param, value):
    """Validate and parse auth rules file (Click callback)

    :param ctx: Click context
    :type  ctx: class:`click.Context`
    :param param: Click params
    :type  param: dict
    :param value: auth config file
    :type  value: class:`click.File`

    :return: validated and parsed auth config
    :rtype:  class:`configparser.ConfigParser`
    """
    try:
        return load_config_auth(load_config(value))
    except (Exception):
        raise click.BadParameter('incorrect configuration format')


def click_validate_config_rules(ctx, param, value):
    """Validate and parse config rules file (Click callback)

    :param ctx: Click context
    :type  ctx: class:`click.Context`
    :param param: Click params
    :type  param: dict
    :param value: rules config file
    :type  value: class:`click.File`

    :return: validated and parsed rules config
    :rtype:  class:`configparser.ConfigParser`
    """
    try:
        return load_config_rules(load_config(value))
    except (Exception):
        raise click.BadParameter('incorrect configuration format')


def click_validate_reposlug(ctx, param, value):
    """Validate reposlug (Click callback)

    :param ctx: Click context
    :type  ctx: class:`click.Context`
    :param param: Click params
    :type  param: dict
    :param value: reposlug to validate
    :type  value: str

    :return: validated reposlug
    :rtype:  str
    """
    rgx = '^[^/ ]+/[^/ ]+$'  # name/repo
    if not re.search(rgx, value):
        raise click.BadParameter('not in owner/repository format')
    return value


def batch_process(config, reposlug, session=requests.Session()):
    """Process all issues in a repo

    :param config: full configuration
    :type  config: class:`configparser.ConfigParser`
    :param reposlug: owner/repository GitHub reposlug
    :type  reposlug: str
    :param session: current session
    :type  session: class:`requests.sessions.Session`, optional
    """

    token = config['github']['token']
    issues = gather_issues(session, reposlug, token)

    for issue in issues:
        if issue['state'] == 'closed':
            continue
        click.echo("-> {} ({})".format(
            click.style(f"{reposlug}#{issue['number']}", bold=True),
            issue['html_url']
        ))
        process_issue(session, issue, config, verbose=True)


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
def main_cmd(strategy, dry_run, config_auth, config_rules, reposlug):
    """CLI tool for automatic issue assigning of GitHub issues"""

    config = {**config_auth, **config_rules}
    config['strategy'] = strategy
    config['dry_run'] = dry_run

    batch_process(config, reposlug)


def main():
    """CLI entrypoint, initializes the Click main command"""

    main_cmd(prog_name='ghia')
