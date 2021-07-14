from enum import Enum
from urllib.parse import urlparse, parse_qs

from flask import Blueprint, request, redirect, url_for

from odp.config import config
from odp.db.models import User
from odp.identity import hydra_admin
from odp.identity.views import hydra_error_page, encode_token
from odp.lib import exceptions as x
from odp.lib.auth import get_token_data

bp = Blueprint('hydra', __name__)


class LoginMode(Enum):
    LOGIN = 'login'
    SIGNUP = 'signup'

    @classmethod
    def from_login_request(cls, login_request):
        url = login_request['request_url']
        try:
            return LoginMode(parse_qs(urlparse(url).query).get('mode', [])[0])
        except (IndexError, ValueError):
            return LoginMode.LOGIN


class Brand(Enum):
    SAEON = 'saeon'
    DFFE = 'dffe'

    @classmethod
    def from_login_request(cls, login_request):
        client_id = login_request['client']['client_id']
        if client_id == config.ODP.IDENTITY.DFFE_BRAND_CLIENT_ID:
            return Brand.DFFE

        return Brand.SAEON


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
        mode = LoginMode.from_login_request(login_request)
        brand = Brand.from_login_request(login_request).value

        if mode == LoginMode.LOGIN:
            target_endpoint = 'login.login'
        elif mode == LoginMode.SIGNUP:
            target_endpoint = 'signup.signup'
        else:
            raise ValueError

        token = encode_token('login', challenge, brand)
        redirect_to = url_for(target_endpoint, token=token)
        return redirect(redirect_to)

    except x.HydraAdminError as e:
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
        user = User.query.get(user_id)
        access_token_data, id_token_data = get_token_data(user, consent_request['requested_scope'])

        consent_params = {
            'grant_scope': consent_request['requested_scope'],
            'grant_audience': consent_request['requested_access_token_audience'],
            'access_token_data': access_token_data.dict(),
            'id_token_data': id_token_data.dict(),
        }
        redirect_to = hydra_admin.accept_consent_request(challenge, **consent_params)

        return redirect(redirect_to)

    except x.HydraAdminError as e:
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

    except x.HydraAdminError as e:
        return hydra_error_page(e)
