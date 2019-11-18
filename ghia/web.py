import requests
import hmac
import os
import click
from flask import Flask, Blueprint, current_app, config, request, abort, render_template
from .helpers import load_config_multiple
from .github import get_gh_login, process_issue


# Initialize app
index_bp = Blueprint('index', __name__)
app_hook_issues_action_wl = ['opened', 'edited', 'transferred', 'reopened',
                             'assigned', 'unassigned', 'labeled', 'unlabeled']


# Gather config
def create_app(session=requests.Session()):
    app = Flask(__name__)
    app.register_blueprint(index_bp)
    # Fetch configuration
    dry_run = 'GHIA_DRYRUN' in os.environ
    env_strategy = os.environ.get('GHIA_STRATEGY')
    strategy = env_strategy if env_strategy in ['set', 'change'] else 'append'
    env_conf = os.environ.get('GHIA_CONFIG')

    config = load_config_multiple(env_conf)
    if not config:
        click.echo("Bad config", err=True)
        exit(10)

    login = get_gh_login(session, config['github']['token'])
    if not login:
        click.echo("Invalid token", err=True)
        exit(10)

    app.config['ghia'] = config
    app.config['ghia']['login'] = login
    app.config['ghia']['strategy'] = strategy
    app.config['ghia']['dry_run'] = dry_run

    return app


# The default web entry point
@index_bp.route('/', methods=['GET', 'POST'])
def index():
    config = current_app.config['ghia']

    if request.method == 'GET':
        return render_template('index.html', config=config)

    # Validate request
    if not webapp_gh_validate():
        abort(403)

    # Respond to ping and issue events
    event = request.headers.get('X-GitHub-Event')
    if event == 'ping':
        return '', 200

    if event == 'issues':
        return webapp_gh_issue_handler()

    abort(404)


# Webhook issue handler
def webapp_gh_issue_handler():
    payload = request.json
    # Only act on specific actions
    if payload['action'] not in app_hook_issues_action_wl:
        return '', 200

    issue = payload['issue']
    if not process_issue(requests.Session(), issue, current_app.config['ghia']):
        abort(400, description='Received issue cannot be processed')
    return '', 200


# Validate github webhook if applicable
def webapp_gh_validate():
    conf = current_app.config['ghia']
    # If secret is not set, do not authenticate
    if 'secret' not in conf['github']:
        return True

    secret = conf['github']['secret']
    sign_hdr = request.headers.get('X-Hub-Signature')

    # Signature is mandatory
    if not sign_hdr:
        return False

    algo, sign = sign_hdr.split('=')
    dg = hmac.new(secret.encode('utf8'), request.data, algo)
    print(request.data, algo, dg.hexdigest())
    return hmac.compare_digest(dg.hexdigest(), sign)
