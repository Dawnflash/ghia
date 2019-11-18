from ghia.web import create_app, webapp_gh_issue_handler, webapp_gh_validate
from helpers import init_flask_env, mkauth, mkauth_default, auth_default, get_user
import pytest
import betamax
import os


@pytest.fixture
def app(betamax_session):
    init_flask_env()
    app = create_app(betamax_session)
    app.config['TESTING'] = True
    return app


def test_create_app_default(app):
    assert app is not None
    assert 'ghia' in app.config
    assert app.config['ghia']['strategy'] == "append"
    assert app.config['ghia']['dry_run'] is False


@pytest.mark.parametrize("strategy,dryrun", [("change", True), ("set", False)])
def test_create_app_param(strategy, dryrun, app):
    conf_bak = app.config['ghia'].copy()
    app.config['ghia']['strategy'] = strategy
    app.config['ghia']['dry_run'] = dryrun
    assert app is not None
    assert 'ghia' in app.config
    assert app.config['ghia']['strategy'] == strategy
    assert app.config['ghia']['dry_run'] is dryrun
    app.config['ghia'] = conf_bak


@pytest.mark.parametrize("needle", ["ghia", "on", "append", "rules", get_user().lower()])
def test_get(needle, app):
    gind = app.test_client().get('/')

    assert gind.status_code == 200
    assert needle in gind.get_data(as_text=True).lower()


def test_post(app):
    # remove the secret
    secret = app.config['ghia']['github'].pop('secret', None)
    client = app.test_client()

    pind = client.post('/')
    assert pind.status_code == 404

    pind = client.post('/', headers={
        'X-GitHub-Event': 'ping'
    })
    assert pind.status_code == 200

    pind = client.post('/', headers={
        'X-GitHub-Event': 'issues',
    }, json={
        'action': 'UNKNOWN_ACTION'
    })
    assert pind.status_code == 200
    if secret:
        app.config['ghia']['github']['secret'] = secret


def test_secret_validation(app):
    # signature for 40*f secret and empty request body
    sign = '03d77323702811c39a628a4f05ead1a89c76c74d'
    client = app.test_client()

    pind = client.post('/', headers={
        'X-GitHub-Event': 'ping',
    })
    assert pind.status_code == 403

    pind = client.post('/', headers={
        'X-GitHub-Event': 'ping',
        'X-Hub-Signature': f"sha1={sign}"
    })
    assert pind.status_code == 200
