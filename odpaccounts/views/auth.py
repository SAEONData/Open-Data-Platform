from flask import Blueprint, request, render_template, flash, redirect, abort, current_app
from flask.helpers import get_env
import requests

from ..models.user import User

bp = Blueprint('auth', __name__)


def check_password(input_text, stored_hash):
    return input_text == stored_hash  # TODO hash...


def validate_auth_response(response):
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        current_app.logger.critical("Auth server returned {} {}", e.response.status_code, e.response.reason)
        abort(500)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    hydra_url = current_app.config['HYDRA_ADMIN_URL']
    ignore_cert_err = get_env() == 'development'

    challenge = request.args.get('login_challenge')
    allow = True
    if request.method == 'GET':
        r = requests.get(hydra_url + '/oauth2/auth/requests/login',
                         params={'login_challenge': challenge},
                         verify=not ignore_cert_err,
                         )
        validate_auth_response(r)
        login_request = r.json()
        authenticated = login_request['skip']
        if authenticated:
            user_id = login_request['subject']
            user = User.query.filter_by(id=user_id).first()
        else:
            return render_template('login.html')
    else:
        # TODO 3rd party login options
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            allow = False
            flash("Incorrect email address", category='error')
            # return render_template('auth/login.html')
        elif not check_password(password, user.password):
            allow = False
            flash("Incorrect password", category='error')
            # return render_template('auth/login.html')
        user_id = user.id if user else None

    allow = allow and user and user.active

    if allow:
        r = requests.put(hydra_url + '/oauth2/auth/requests/login/accept',
                         params={'login_challenge': challenge},
                         verify=not ignore_cert_err,
                         json={
                             'subject': user_id,
                             'remember': True,
                             'remember_for': 7 * 24 * 3600,  # remember the user for 1 week
                         })
    else:
        r = requests.put(hydra_url + '/oauth2/auth/requests/login/reject',
                         params={'login_challenge': challenge},
                         verify=not ignore_cert_err,
                         json={
                             'error': 'unknown_user',
                             'error_description': "Unknown user",
                         })

    validate_auth_response(r)
    redirect_to = r.json()['redirect_to']
    return redirect(redirect_to)


@bp.route('/consent')
def consent():
    hydra_url = current_app.config['HYDRA_ADMIN_URL']
    ignore_cert_err = get_env() == 'development'

    challenge = request.args.get('consent_challenge')
    r = requests.get(hydra_url + '/oauth2/auth/requests/consent',
                     params={'consent_challenge': challenge},
                     verify=not ignore_cert_err,
                     )
    validate_auth_response(r)
    consent_request = r.json()
    user_id = consent_request['subject']
    user = User.query.filter_by(id=user_id).one()

    r = requests.put(hydra_url + '/oauth2/auth/requests/consent/accept',
                     params={'consent_challenge': challenge},
                     verify=not ignore_cert_err,
                     json={
                         'grant_scope': consent_request['requested_scope'],
                         'grant_access_token_audience': consent_request['requested_access_token_audience'],
                         'remember': False,  # we're not showing a consent UI (because all our clients are first-party), so this is irrelevant
                         'session': {
                             'access_token': {},
                             'id_token': {
                                 'email': user.email,
                             },
                         },
                     })
    validate_auth_response(r)
    redirect_to = r.json()['redirect_to']
    return redirect(redirect_to)


@bp.route('/logout')
def logout():
    hydra_url = current_app.config['HYDRA_ADMIN_URL']
    ignore_cert_err = get_env() == 'development'

    challenge = request.args.get('logout_challenge')
    r = requests.get(hydra_url + '/oauth2/auth/requests/logout',
                     params={'logout_challenge': challenge},
                     verify=not ignore_cert_err,
                     )
    validate_auth_response(r)
    logout_request = r.json()
    user_id = logout_request['subject']

    r = requests.put(hydra_url + '/oauth2/auth/requests/logout/accept',
                     params={'logout_challenge': challenge},
                     verify=not ignore_cert_err,
                     )
    validate_auth_response(r)
    redirect_to = r.json()['redirect_to']
    return redirect(redirect_to)
