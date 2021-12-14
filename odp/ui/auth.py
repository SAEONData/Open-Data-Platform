import redis
from flask import Flask
from flask_login import LoginManager

from odp import ODPScope
from odp.config import config
from odp.db import Session
from odp.db.models import User
from odp.lib.oauth2 import FlaskOAuth2Client

login_manager = LoginManager()

oauth2 = FlaskOAuth2Client(
    hydra_url=config.HYDRA.PUBLIC.URL,
    client_id=config.ODP.UI.CLIENT_ID,
    client_secret=config.ODP.UI.CLIENT_SECRET,
    scope=['openid', 'offline'] + [s.value for s in ODPScope],
    cache=redis.Redis(
        host=config.REDIS.HOST,
        port=config.REDIS.PORT,
        db=config.REDIS.DB,
        decode_responses=True,
    )
)


def init_app(app: Flask):
    login_manager.init_app(app)
    oauth2.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Session.get(User, user_id)
