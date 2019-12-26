
"""Logic of the CLI batch interface
"""

import requests
import asyncio
import aiohttp
import click
import re
from .helpers import load_config, load_config_auth, load_config_rules
from .github import gather_issues, gather_issues_async, process_issue


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
    """Validate reposlugs (Click callback)

    :param ctx: Click context
    :type  ctx: class:`click.Context`
    :param param: Click params
    :type  param: dict
    :param value: reposlugs to validate
    :type  value: tuple

    :return: validated reposlugs
    :rtype:  str
    """
    rgx = re.compile('^[^/ ]+/[^/ ]+$')  # name/repo
    for val in value:
        if not rgx.fullmatch(val):
            raise click.BadParameter('not in owner/repository format')
    return value


def batch_process(config, reposlugs):
    """Process all issues in given repos synchronously

    :param config: full configuration
    :type  config: class:`configparser.ConfigParser`
    :param reposlugs: owner/repository GitHub reposlugs
    :type  reposlugs: tuple
    """

    token = config['github']['token']
    session = requests.Session()

    # issue gathering
    for reposlug in reposlugs:
        issues = gather_issues(session, reposlug, token)

        # issue processing
        for issue in issues:
            if issue['state'] == 'closed':
                continue
            click.echo("-> {} ({})".format(
                click.style(f"{reposlug}#{issue['number']}", bold=True),
                issue['html_url']
            ))
            process_issue(session, issue, config, verbose=True)


async def batch_process_async(config, reposlugs):
    """Process all issues in given repos asynchronously

    :param config: full configuration
    :type  config: class:`configparser.ConfigParser`
    :param reposlugs: owner/repository GitHub reposlugs
    :type  reposlugs: tuple
    """

    token = config['github']['token']

    async with aiohttp.ClientSession() as session:
        async def proc_issue(issue, reposlug):
            issue['ghia_output'] = "-> {} ({})\n".format(
                click.style(f"{reposlug}#{issue['number']}", bold=True),
                issue['html_url']
            )
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, process_issue, session, issue, config, True
            )
            # process_issue(session, issue, config, True)

        cors = [gather_issues_async(session, reposlug, token) for reposlug in reposlugs]
        icors = []
        issues_all = await asyncio.gather(*cors)
        for issues, reposlug in zip(issues_all, reposlugs):
            for issue in issues:
                icors.append(proc_issue(issue, reposlug))
        await asyncio.gather(*icors)


@click.command()
@click.option('-s', '--strategy', help='How to handle assignment collisions.',
              type=click.Choice(['append', 'set', 'change']),
              default='append', show_default=True)
@click.option('-d', '--dry-run', help='Run without making any changes.', is_flag=True)
@click.option('-x', '--async', 'is_async', help='Process repos and issues asynchronously.', is_flag=True)
@click.option('-a', '--config-auth', help='File with authorization configuration.',
              required=True, type=click.File('r'), callback=click_validate_config_auth)
@click.option('-r', '--config-rules', help='File with assignment rules configuration.',
              required=True, type=click.File('r'), callback=click_validate_config_rules)
@click.argument('reposlug', callback=click_validate_reposlug, nargs=-1, required=True)
def main_cmd(strategy, dry_run, is_async, config_auth, config_rules, reposlug):
    """CLI tool for automatic issue assigning of GitHub issues"""

    config = {**config_auth, **config_rules}
    config['strategy'] = strategy
    config['dry_run'] = dry_run

    if is_async:
        asyncio.run(batch_process_async(config, reposlug))
    else:
        batch_process(config, reposlug)


def main():
    """CLI entrypoint, initializes the Click main command"""

    main_cmd(prog_name='ghia')
