from flask import Blueprint, request, render_template, redirect, abort, current_app
from flask.helpers import get_env
from hydra import HydraAdminClient, HydraAdminError

from odpaccounts.db import session as db_session
from odpaccounts.models.user import User

from ..forms.login import LoginForm
from ..lib.users import validate_auto_login, id_token_data, access_token_data
from ..lib import exceptions as x

bp = Blueprint('auth', __name__)


def create_hydra_admin():
    """
    Returns a HydraAdminClient instance.
    """
    return HydraAdminClient(
        server_url=current_app.config['HYDRA_ADMIN_URL'],
        remember_login_for=current_app.config['HYDRA_LOGIN_EXPIRY'],
        verify_tls=get_env() != 'development',
    )


def hydra_error(e):
    """
    Requests to the Hydra admin API are critical to the login, consent and logout flows.
    If anything is wrong with any response from Hydra, we abort - raising an internal
    server error.

    :param e: the HydraAdminError exception
    """
    current_app.logger.critical("Hydra server %d error for %s %s: %s",
                                e.status_code, e.method, e.endpoint, e.error_detail)
    abort(500)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Redirected here from Hydra as part of the login flow.
    """
    try:
        hydra_admin = create_hydra_admin()
        user_id = None
        error = None
        form = None

        if request.method == 'GET':
            # we should only ever get here by a redirect from Hydra; if a user tries to get
            # this endpoint, they won't have a valid challenge and we'll end up aborting
            challenge = request.args.get('login_challenge')
            login_request = hydra_admin.get_login_request(challenge)
            authenticated = login_request['skip']

            # if already authenticated, we'll wind up with either a user_id or an error
            if authenticated:
                user_id = login_request['subject']
                try:
                    validate_auto_login(user_id)
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
            redirect_to = hydra_admin.accept_login_request(challenge, user_id)
        elif error:
            redirect_to = hydra_admin.reject_login_request(challenge, error.error_code, error.error_description)
        else:
            return render_template('login.html', form=form)

        return redirect(redirect_to)

    except HydraAdminError as e:
        hydra_error(e)


@bp.route('/consent')
def consent():
    """
    Redirected here from Hydra as part of the consent flow.
    """
    try:
        hydra_admin = create_hydra_admin()
        challenge = request.args.get('consent_challenge')
        consent_request = hydra_admin.get_consent_request(challenge)
        user_id = consent_request['subject']
        user = db_session.query(User).get(user_id)

        consent_params = {
            'grant_scope': consent_request['requested_scope'],
            'grant_audience': consent_request['requested_access_token_audience'],
            'access_token_data': access_token_data(user, consent_request['requested_scope']),
            'id_token_data': id_token_data(user),
        }
        redirect_to = hydra_admin.accept_consent_request(challenge, **consent_params)

        return redirect(redirect_to)

    except HydraAdminError as e:
        hydra_error(e)


@bp.route('/logout')
def logout():
    """
    Redirected here from Hydra as part of the logout flow.
    """
    try:
        hydra_admin = create_hydra_admin()
        challenge = request.args.get('logout_challenge')
        logout_request = hydra_admin.get_logout_request(challenge)
        redirect_to = hydra_admin.accept_logout_request(challenge)
        return redirect(redirect_to)

    except HydraAdminError as e:
        hydra_error(e)
