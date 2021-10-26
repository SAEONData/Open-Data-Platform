from functools import wraps

import redis
from authlib.integrations.flask_client import OAuth
from flask import g
from flask_login import LoginManager, current_user
from sqlalchemy import select
from werkzeug.exceptions import abort

from odp import ODPScope
from odp.config import config
from odp.db import Session
from odp.db.models import User, OAuth2Token
from odp.lib.auth import get_user_auth

login_manager = LoginManager()
login_manager.login_view = 'hydra.login'

oauth = OAuth()


@login_manager.user_loader
def load_user(user_id):
    return Session.get(User, user_id)


def init_app(app):
    login_manager.init_app(app)
    cache = redis.Redis(
        host=config.REDIS.HOST,
        port=config.REDIS.PORT,
        db=config.REDIS.DB,
        decode_responses=True,
    )
    oauth.init_app(app, cache, fetch_token, update_token)
    oauth.register(
        name='hydra',
        access_token_url=f'{(hydra_url := config.HYDRA.PUBLIC.URL)}/oauth2/token',
        authorize_url=f'{hydra_url}/oauth2/auth',
        userinfo_endpoint=f'{hydra_url}/userinfo',
        client_id=config.ODP.APP.CLIENT_ID,
        client_secret=config.ODP.APP.CLIENT_SECRET,
        client_kwargs={'scope': ' '.join(['openid', 'offline'] + [s.value for s in ODPScope])},
    )


def authorize(scope: ODPScope):
    """Decorator for authorizing access to a view."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)

            g.user_auth = get_user_auth(current_user.id, config.ODP.APP.CLIENT_ID)
            if scope not in g.user_auth.scopes:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def fetch_token(hydra_name):
    return Session.get(OAuth2Token, current_user.id).dict()


def update_token(hydra_name, token, refresh_token=None, access_token=None):
    if refresh_token:
        token_model = Session.execute(
            select(OAuth2Token).
            where(OAuth2Token.refresh_token == refresh_token)
        ).one()
    elif access_token:
        token_model = Session.execute(
            select(OAuth2Token).
            where(OAuth2Token.access_token == access_token)
        ).one()
    else:
        return

    token_model.access_token = token.get('access_token')
    token_model.refresh_token = token.get('refresh_token')
    token_model.expires_at = token.get('expires_at')
    token_model.save()
