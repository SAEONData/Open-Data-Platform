from flask import Blueprint, request, render_template, redirect, abort, current_app
from flask.helpers import get_env
import requests

from ..models.user import User
from ..forms.login import LoginForm
from ..lib.users import validate_auto_login
from ..lib import exceptions as x

bp = Blueprint('auth', __name__)


def validate_hydra_response(response):
    """
    Requests to the Hydra admin API are critical to the login, consent and logout flows.
    If anything is wrong with any response from Hydra, we abort - raising an internal
    server error.
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        current_app.logger.critical("Hydra server returned %d %s", e.response.status_code, e.response.reason)
        abort(500)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Called by Hydra as part of the login flow.
    """
    hydra_url = current_app.config['HYDRA_ADMIN_URL']
    ignore_cert_err = get_env() == 'development'

    user_id = None
    error = None
    form = None

    if request.method == 'GET':
        # we'll only ever get here by a request from Hydra; if a user tries to get
        # this endpoint, they won't have a valid challenge and we'll end up aborting
        challenge = request.args.get('login_challenge')

        r = requests.get(hydra_url + '/oauth2/auth/requests/login',
                         params={'login_challenge': challenge},
                         verify=not ignore_cert_err,
                         )
        validate_hydra_response(r)
        login_request = r.json()
        authenticated = login_request['skip']

        # if already authenticated, we'll wind up with either a user_id or an error
        if authenticated:
            user_id = login_request['subject']
            try:
                validate_auto_login(user_id)
            # except x.ODPUserNotFound:
            #     todo: delete user session on hydra
            except x.ODPLoginError as e:
                user_id = None
                error = e

        # otherwise, we prepare a login form
        else:
            form = LoginForm(login_challenge=challenge)

    else:
        # it's a post from the user
        form = LoginForm()
        challenge = form.login_challenge.data
        try:
            if form.validate():  # calls validate_user_login
                user_id = form.user_id
        except x.ODPLoginError as e:
            error = e

    if user_id:
        r = requests.put(hydra_url + '/oauth2/auth/requests/login/accept',
                         params={'login_challenge': challenge},
                         verify=not ignore_cert_err,
                         json={
                             'subject': user_id,
                             'remember': True,
                             'remember_for': 7 * 24 * 3600,  # remember the user for 1 week
                         })
    elif error:
        r = requests.put(hydra_url + '/oauth2/auth/requests/login/reject',
                         params={'login_challenge': challenge},
                         verify=not ignore_cert_err,
                         json={
                             'error': error.error_code,
                             'error_description': error.error_description,
                         })
    else:
        return render_template('login.html', form=form)

    validate_hydra_response(r)
    redirect_to = r.json()['redirect_to']
    return redirect(redirect_to)


@bp.route('/consent')
def consent():
    """
    Called by Hydra as part of the consent flow.
    """
    hydra_url = current_app.config['HYDRA_ADMIN_URL']
    ignore_cert_err = get_env() == 'development'
    challenge = request.args.get('consent_challenge')

    r = requests.get(hydra_url + '/oauth2/auth/requests/consent',
                     params={'consent_challenge': challenge},
                     verify=not ignore_cert_err,
                     )
    validate_hydra_response(r)
    consent_request = r.json()
    user_id = consent_request['subject']
    user = User.query.get(user_id)

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
    validate_hydra_response(r)
    redirect_to = r.json()['redirect_to']
    return redirect(redirect_to)


@bp.route('/logout')
def logout():
    """
    Called by Hydra as part of the logout flow.
    """
    hydra_url = current_app.config['HYDRA_ADMIN_URL']
    ignore_cert_err = get_env() == 'development'
    challenge = request.args.get('logout_challenge')

    r = requests.get(hydra_url + '/oauth2/auth/requests/logout',
                     params={'logout_challenge': challenge},
                     verify=not ignore_cert_err,
                     )
    validate_hydra_response(r)
    logout_request = r.json()
    user_id = logout_request['subject']

    r = requests.put(hydra_url + '/oauth2/auth/requests/logout/accept',
                     params={'logout_challenge': challenge},
                     verify=not ignore_cert_err,
                     )
    validate_hydra_response(r)
    redirect_to = r.json()['redirect_to']
    return redirect(redirect_to)
