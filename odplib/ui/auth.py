import redis
from flask import Flask
from flask_login import LoginManager

from odp.config import config
from odp.db import Session
from odp.db.models import User
from odp.lib.oauth2 import FlaskOAuth2Client

login_manager = LoginManager()
oauth2 = FlaskOAuth2Client()


def init_app(app: Flask):
    login_manager.init_app(app)
    oauth2.init_app(
        app,
        hydra_url=config.HYDRA.PUBLIC.URL,
        client_id=app.config['CLIENT_ID'],
        client_secret=app.config['CLIENT_SECRET'],
        scope=app.config['CLIENT_SCOPE'],
        cache=redis.Redis(
            host=config.REDIS.HOST,
            port=config.REDIS.PORT,
            db=config.REDIS.DB,
            decode_responses=True,
        )
    )


@login_manager.user_loader
def load_user(user_id):
    return Session.get(User, user_id)
