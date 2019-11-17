from ghia.helpers import load_config, load_config_auth, load_config_rules, load_config_multiple
from helpers import config, mkauth, mkauth_default


def lconf(name):
    conf_file = open(config(name))
    return load_config(conf_file)


def test_load_config_auth():
    conf = lconf('auth')
    assert conf is not None
    cdict = load_config_auth(conf)
    assert type(cdict) is dict
    assert 'github' in cdict
    assert 'secret' in cdict['github']

    mkauth('default', None)
    conf = lconf('auth')
    cdict = load_config_auth(conf)
    assert 'secret' not in cdict['github']
    mkauth_default()


def test_load_config_rules():
    conf = lconf('rules')
    assert conf is not None
    cdict = load_config_rules(conf)
    assert type(cdict) is dict
    assert 'patterns' in cdict
    assert 'fallback' in cdict


def test_load_config_multiple():
    conf = load_config_multiple(f"{config('auth')}:{config('rules')}")
    assert conf is not None
    conf = load_config_multiple(f"{config('auth')}:{config('auth')}")
    assert conf is None
    conf = load_config_multiple(f"{config('rules')}:{config('rules')}")
    assert conf is None
