from flask import current_app, redirect, url_for, flash, abort
from itsdangerous import JSONWebSignatureSerializer, BadData

from .. import hydra_admin


def init_app(app):
    from . import home, user, hydra_oauth2, hydra_integration, login, signup, account

    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(login.bp, url_prefix='/login')
    app.register_blueprint(signup.bp, url_prefix='/signup')
    app.register_blueprint(account.bp, url_prefix='/account')
    app.register_blueprint(hydra_oauth2.bp, url_prefix='/oauth2')
    app.register_blueprint(hydra_integration.bp, url_prefix='/hydra')


def encode_token(challenge: str, scope: str, **params):
    """
    Create a JWS token for accessing application views (other than the Hydra workflow views)
    which may only be accessed within the context of the Hydra login workflow.

    :param challenge: the Hydra login challenge
    :param scope: the scope for which the token is valid;
        This enables a given token to be re-used across multiple views, but only where those
        views expect the same token scope. So we might, for example, allow a user to switch
        between login and signup views with the same token, but prevent them from copying a
        password reset token and passing it to the email verification view.
    :param params: any additional params to pass to the view
    :return: a JSON Web Signature
    """
    serializer = JSONWebSignatureSerializer(current_app.secret_key, salt=scope)
    params.update({'challenge': challenge})
    token = serializer.dumps(params)
    return token


def decode_token(token: str, scope: str):
    """
    Decode and validate a JWS token received by a view, and return the Hydra login
    request dict and login challenge, along with any additional params.

    :param token: the token to decode
    :param scope: the scope for which the token is valid
    :return: tuple(login_request: dict, login_challenge: str, view_params: dict)
    :raises HydraAdminError: if the encoded login challenge is invalid
    """
    if not token:
        abort(403)  # HTTP 403 Forbidden

    try:
        serializer = JSONWebSignatureSerializer(current_app.secret_key, salt=scope)
        params = serializer.loads(token)
        challenge = params.pop('challenge', '')
        login_request = hydra_admin.get_login_request(challenge)
        return login_request, challenge, params

    except BadData:
        abort(403)  # HTTP 403 Forbidden


def hydra_error_page(e):
    """
    Requests to the Hydra admin API are critical to the login, consent and logout flows.
    If anything is wrong with any response from Hydra, we abort - redirecting the user
    home.

    :param e: the HydraAdminError exception
    :return: a redirect response
    """
    if 400 <= e.status_code < 500:
        current_app.logger.error("Hydra client %d error for %s %s: %s",
                                 e.status_code, e.method, e.endpoint, e.error_detail)
    elif 500 <= e.status_code < 600:
        current_app.logger.critical("Hydra server %d error for %s %s: %s",
                                    e.status_code, e.method, e.endpoint, e.error_detail)
    else:
        raise ValueError  # HydraAdminError should only ever be raised for HTTP 4xx/5xx errors

    flash("There was a problem with your request. Our technicians have been notified.", category='error')
    return redirect(url_for('home.index'))
