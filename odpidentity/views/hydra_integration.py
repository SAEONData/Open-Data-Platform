from enum import Enum
from urllib.parse import urlparse, parse_qs

from flask import Blueprint, request, redirect, abort, url_for
from hydra import HydraAdminError

from odpaccounts.db import session as db_session
from odpaccounts.models.user import User

from ..lib.users import id_token_data, access_token_data
from ..lib.hydra import hydra_error_page
from . import hydra_admin

bp = Blueprint('hydra', __name__)


class LoginMode(Enum):
    LOGIN = 'login'
    SIGNUP = 'signup'

    @classmethod
    def from_request_url(cls, url):
        try:
            return LoginMode(parse_qs(urlparse(url).query).get('mode', [])[0])
        except (IndexError, ValueError):
            abort(422)  # HTTP 422 Unprocessable Entity


@bp.route('/login')
def login():
    """
    Redirected here from Hydra as part of the login flow.
    """
    try:
        challenge = request.args.get('login_challenge')
        login_request = hydra_admin.get_login_request(challenge)
        login_mode = LoginMode.from_request_url(login_request['request_url'])

        if login_mode == LoginMode.LOGIN:
            return redirect(url_for('user.login', challenge=challenge))
        elif login_mode == LoginMode.SIGNUP:
            return redirect(url_for('user.signup', challenge=challenge))
        else:
            abort(501)  # HTTP 501 Not Implemented

    except HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/consent')
def consent():
    """
    Redirected here from Hydra as part of the consent flow.
    """
    try:
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
        return hydra_error_page(e)


@bp.route('/logout')
def logout():
    """
    Redirected here from Hydra as part of the logout flow.
    """
    try:
        challenge = request.args.get('logout_challenge')
        logout_request = hydra_admin.get_logout_request(challenge)
        redirect_to = hydra_admin.accept_logout_request(challenge)
        return redirect(redirect_to)

    except HydraAdminError as e:
        return hydra_error_page(e)
