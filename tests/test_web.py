from ghia.web import create_app, webapp_gh_issue_handler, webapp_gh_validate
from helpers import inject_flask_env, mkauth, mkauth_default, auth_default
import pytest


def tclient():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_create_app_default():
    inject_flask_env()
    app = create_app()
    assert app is not None
    assert 'ghia' in app.config
    assert app.config['ghia']['strategy'] == "append"
    assert app.config['ghia']['dry_run'] is False


@pytest.mark.parametrize("strategy,dryrun", [("change", True), ("set", False)])
def test_create_app_param(strategy, dryrun):
    inject_flask_env(strategy, dryrun)
    app = create_app()
    assert app is not None
    assert 'ghia' in app.config
    assert app.config['ghia']['strategy'] == strategy
    assert app.config['ghia']['dry_run'] is dryrun


@pytest.mark.parametrize("needle", ["ghia", "on", "change", "rules"])
def test_get(needle):
    mkauth(auth_default()[0], None)
    inject_flask_env("change", True)
    gind = tclient().get('/')

    assert gind.status_code == 200
    assert needle in gind.get_data(as_text=True).lower()
    mkauth_default()


def test_post():
    mkauth(auth_default()[0], None)
    inject_flask_env()
    client = tclient()

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
    mkauth_default()


def test_secret_validation():
    # signature for 40*f secret and empty request body
    sign = '03d77323702811c39a628a4f05ead1a89c76c74d'
    print(auth_default()[1])
    inject_flask_env()
    client = tclient()

    pind = client.post('/', headers={
        'X-GitHub-Event': 'ping',
    })
    assert pind.status_code == 403

    pind = client.post('/', headers={
        'X-GitHub-Event': 'ping',
        'X-Hub-Signature': f"sha1={sign}"
    })
    assert pind.status_code == 200
