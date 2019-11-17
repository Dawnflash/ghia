import os
import pathlib
import atexit


def config(name):
    return pathlib.Path(__file__).parent / 'fixtures' / f"{name}.cfg"


def mkauth(token, secret):
    conf = '[github]\n'
    if token is not None:
        conf += f"token={token}\n"
    if secret is not None:
        conf += f"secret={secret}\n"
    config('auth').write_text(conf)


def mkauth_default():
    token, secret = 40 * 'f', 40 * 'f'
    if 'GITHUB_TOKEN' in os.environ:
        token = os.environ['GITHUB_TOKEN']
    if 'GITHUB_SECRET' in os.environ:
        secret = os.environ['GITHUB_SECRET']
    mkauth(token, secret)


def repo():
    if 'GITHUB_REPO' in os.environ:
        return os.environ['GITHUB_REPO']
    return None


mkauth_default()
atexit.register(config('auth').unlink)
