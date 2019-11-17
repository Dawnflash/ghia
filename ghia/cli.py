import click
import re
from .helpers import load_config, load_config_auth, load_config_rules
from .github import gather_issues, process_issue


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
def main_cmd(strategy, dry_run, config_auth, config_rules, reposlug):
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


def main():
    main_cmd(prog_name='ghia')
