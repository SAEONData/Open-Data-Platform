from enum import Enum
from urllib.parse import urlparse, parse_qs

from flask import Blueprint, request, redirect, abort, url_for
from hydra import HydraAdminError

from odpaccounts.db import session as db_session
from odpaccounts.models.user import User
from odpaccounts.authorization.utils import get_access_rights, get_user_profile

from . import hydra_error_page, encode_token
from .. import hydra_admin

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
    Implements the login provider component of the Hydra login workflow.
    Hydra redirects to this endpoint based on the ``URLS_LOGIN`` environment
    variable configured on the Hydra server.
    """
    try:
        challenge = request.args.get('login_challenge')
        login_request = hydra_admin.get_login_request(challenge)
        login_mode = LoginMode.from_request_url(login_request['request_url'])

        if login_mode == LoginMode.LOGIN:
            target_endpoint = 'login.login'
        elif login_mode == LoginMode.SIGNUP:
            target_endpoint = 'signup.signup'
        else:
            raise ValueError

        token = encode_token(challenge, 'login')
        redirect_to = url_for(target_endpoint, token=token)
        return redirect(redirect_to)

    except HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/consent')
def consent():
    """
    Implements the consent provider component of the Hydra consent workflow.
    Hydra redirects to this endpoint based on the ``URLS_CONSENT`` environment
    variable configured on the Hydra server.
    """
    try:
        challenge = request.args.get('consent_challenge')
        consent_request = hydra_admin.get_consent_request(challenge)
        user_id = consent_request['subject']
        user = db_session.query(User).get(user_id)

        access_rights = get_access_rights(user, consent_request['requested_scope'])
        user_profile = get_user_profile(user)

        consent_params = {
            'grant_scope': consent_request['requested_scope'],
            'grant_audience': consent_request['requested_access_token_audience'],
            'access_token_data': access_rights.dict(),
            'id_token_data': user_profile.dict(),
        }
        redirect_to = hydra_admin.accept_consent_request(challenge, **consent_params)

        return redirect(redirect_to)

    except HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/logout')
def logout():
    """
    Implements the logout provider component of the Hydra logout workflow.
    Hydra redirects to this endpoint based on the ``URLS_LOGOUT`` environment
    variable configured on the Hydra server.
    """
    try:
        challenge = request.args.get('logout_challenge')
        logout_request = hydra_admin.get_logout_request(challenge)
        redirect_to = hydra_admin.accept_logout_request(challenge)
        return redirect(redirect_to)

    except HydraAdminError as e:
        return hydra_error_page(e)
