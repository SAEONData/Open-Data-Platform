from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, request, url_for, redirect

from odp.identity import google_oauth2, hydra_admin
from odp.identity.views import encode_token, decode_token, hydra_error_page
from odp.lib import exceptions as x
from odp.lib.users import validate_google_login

bp = Blueprint('google', __name__)


@bp.route('/login', methods=('POST',))
def login():
    """
    View for authenticating via Google. The token ensures that we can only
    access this view in the context of the Hydra login workflow.
    """
    token = request.args.get('token')
    try:
        login_request, challenge, params = decode_token(token, 'login')
        logged_in_token = encode_token(challenge, 'google.logged_in')
        redirect_uri = url_for('.logged_in', _external=True)
        return google_oauth2.google.authorize_redirect(redirect_uri, state=logged_in_token.decode())

    except x.HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/logged_in')
def logged_in():
    """
    Callback from Google. The token in the 'state' param ensures that this view
    can only be accessed in the context of the Google OAuth2 flow, initiated from
    our Google login view.
    """
    token = request.args.get('state')
    try:
        login_request, challenge, params = decode_token(token, 'google.logged_in')
        try:
            try:
                google_token = google_oauth2.google.authorize_access_token(state=token)
                userinfo = google_oauth2.google.parse_id_token(google_token)
                email = userinfo['email']
                email_verified = userinfo['email_verified']

            except (OAuthError, KeyError):
                raise x.ODPGoogleAuthError

            user_id = validate_google_login(email, email_verified)
            redirect_to = hydra_admin.accept_login_request(challenge, user_id)

        except x.ODPIdentityError as e:
            redirect_to = hydra_admin.reject_login_request(challenge, e.error_code, e.error_description)

        return redirect(redirect_to)

    except x.HydraAdminError as e:
        return hydra_error_page(e)
