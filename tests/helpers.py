import os
import re
import pathlib
import atexit
import betamax
from ghia.helpers import load_config


def fixture(name):
    return pathlib.Path(__file__).parent / 'fixtures' / name


def fetch_issue(issues, no):
    for i in issues:
        if i['number'] == no:
            return i
    return None


def issue_configs():
    configs = []
    label = 'AssignMe'
    user = get_user()
    conf = {
        'github': {
            'token': auth_default()[0]
        },
        'patterns': {
            user: [
                ('title', re.compile('developer')),
                ('any', re.compile('[Dd]atabase')),
                ('label', re.compile('bug')),
                ('text', re.compile('[Pp]ython')),
                ('title', re.compile('workflow')),
            ]
        },
        'strategy': 'append',
        'fallback': {
            'label': label
        },
        'dry_run': False
    }
    # Add fallback label, nothing else
    configs.append((1, conf.copy(), (0, 0, 0), label))
    # Add single user, nothing else
    configs.append((2, conf.copy(), (0, 1, 0), None))
    # Add extra user
    configs.append((7, conf.copy(), (0, 1, 2), None))
    # Assign single user (set)
    conf['strategy'] = 'set'
    configs.append((3, conf.copy(), (0, 1, 0), None))
    configs.append((4, conf.copy(), (0, 1, 0), None))
    # Do nothing (set)
    configs.append((5, conf.copy(), (0, 0, 1), None))
    # Replace user
    conf['strategy'] = 'change'
    configs.append((5, conf.copy(), (1, 1, 0), None))

    return configs


# clean flask env
def init_flask_env():
    os.environ['GHIA_CONFIG'] = f"{fixture('auth.cfg')}:{fixture('rules.cfg')}"
    os.environ.pop('GHIA_STRATEGY', None)
    os.environ.pop('GHIA_DRYRUN', None)


def mkauth(token, secret):
    conf = '[github]\n'
    if token is not None:
        conf += f"token={token}\n"
    if secret is not None:
        conf += f"secret={secret}\n"
    fixture('auth.cfg').write_text(conf)


def auth_default():
    token, secret = 40 * 'f', 40 * 'f'
    if 'GITHUB_TOKEN' in os.environ:
        token = os.environ['GITHUB_TOKEN']
    if 'GITHUB_SECRET' in os.environ:
        secret = os.environ['GITHUB_SECRET']
    return token, secret


def mkauth_default():
    mkauth(*auth_default())


def get_user():
    uf = fixture('user.txt')
    user = uf.read_text().strip()
    if 'GITHUB_USER' in os.environ:
        user = os.environ['GITHUB_USER']
        uf.write_text(user)
    return user


def get_repo():
    return f"mi-pyt-ghia/{get_user()}"


mkauth_default()
atexit.register(fixture('auth.cfg').unlink)
with betamax.Betamax.configure() as config:
    if 'GITHUB_TOKEN' not in os.environ:
        # Do not attempt to record sessions with fake token
        config.default_cassette_options['record_mode'] = 'none'
    # Hide the token in the cassettes
    config.define_cassette_placeholder('<TOKEN>', auth_default()[0])
