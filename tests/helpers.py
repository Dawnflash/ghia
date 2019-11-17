import os
import pathlib
import atexit
from ghia.helpers import load_config


def config(name):
    return pathlib.Path(__file__).parent / 'fixtures' / f"{name}.cfg"


def inject_flask_env(strategy=None, dryrun=None):
    os.environ['GHIA_CONFIG'] = f"{config('auth')}:{config('rules')}"
    if strategy:
        os.environ['GHIA_STRATEGY'] = strategy
    else:
        os.environ.pop('GHIA_STRATEGY', None)
    if dryrun:
        os.environ['GHIA_DRYRUN'] = "on"
    else:
        os.environ.pop('GHIA_DRYRUN', None)


def mkauth(token, secret):
    conf = '[github]\n'
    if token is not None:
        conf += f"token={token}\n"
    if secret is not None:
        conf += f"secret={secret}\n"
    config('auth').write_text(conf)


def auth_default():
    token, secret = 40 * 'f', 40 * 'f'
    if 'GITHUB_TOKEN' in os.environ:
        token = os.environ['GITHUB_TOKEN']
    if 'GITHUB_SECRET' in os.environ:
        secret = os.environ['GITHUB_SECRET']
    return token, secret


def mkauth_default():
    mkauth(*auth_default())


def repo():
    if 'GITHUB_REPO' in os.environ:
        return os.environ['GITHUB_REPO']
    return None


mkauth_default()
atexit.register(config('auth').unlink)
