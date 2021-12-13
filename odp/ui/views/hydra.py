import secrets

from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, url_for, redirect, flash, request
from flask_login import login_user, logout_user, current_user

from odp.config import config
from odp.db import Session
from odp.db.models import User, OAuth2Token
from odp.ui.auth import oauth

bp = Blueprint('hydra', __name__)

_client_id = config.ODP.UI.CLIENT_ID


def _client():
    return getattr(oauth, _client_id)


@bp.route('/signup')
def signup():
    redirect_uri = url_for('.logged_in', _external=True)
    return _client().authorize_redirect(redirect_uri, mode='signup')


@bp.route('/login')
def login():
    redirect_uri = url_for('.logged_in', _external=True)
    return _client().authorize_redirect(redirect_uri, mode='login')


@bp.route('/logged_in')
def logged_in():
    try:
        token = _client().authorize_access_token()
        userinfo = _client().userinfo()
        user_id = userinfo['sub']

        if not (token_model := Session.get(OAuth2Token, (_client_id, user_id))):
            token_model = OAuth2Token(client_id=_client_id, user_id=user_id)

        token_model.token_type = token.get('token_type')
        token_model.access_token = token.get('access_token')
        token_model.refresh_token = token.get('refresh_token')
        token_model.id_token = token.get('id_token')
        token_model.expires_at = token.get('expires_at')
        token_model.save()

        user = Session.get(User, user_id)
        login_user(user)

    except OAuthError as e:
        flash(str(e), category='error')

    return redirect(url_for('home.index'))


@bp.route('/logout')
def logout():
    token = oauth.fetch_token(_client_id)
    state_val = secrets.token_urlsafe()
    oauth.cache.set(_state_key(), state_val, ex=10)
    url = f'{config.HYDRA.PUBLIC.URL}/oauth2/sessions/logout' \
          f'?id_token_hint={token.get("id_token")}' \
          f'&post_logout_redirect_uri={url_for(".logged_out", _external=True)}' \
          f'&state={state_val}'
    return redirect(url)


@bp.route('/logged_out')
def logged_out():
    state_val = request.args.get('state')
    if state_val == oauth.cache.get(key := _state_key()):
        logout_user()
        oauth.cache.delete(key)
    return redirect(url_for('home.index'))


def _state_key():
    return f'{__name__}.{_client_id}.{current_user.id}.state'
