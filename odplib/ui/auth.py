import redis
from flask import Flask
from flask_login import LoginManager

from odp.db import Session
from odp.db.models import User
from odplib.client.system import OAuth2SystemClient
from odplib.client.ui import OAuth2UIClient
from odplib.config import config

login_manager = LoginManager()
oauth2_ui_client = OAuth2UIClient()
oauth2_system_client: OAuth2SystemClient


def init_app(app: Flask):
    login_manager.init_app(app)
    oauth2_ui_client.init_app(
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
    global oauth2_system_client
    oauth2_system_client = OAuth2SystemClient(
        api_url=app.config['API_URL'],
        token_url=f'{config.HYDRA.PUBLIC.URL}/oauth2/token',
        client_id=app.config['SYSTEM_CLIENT_ID'],
        client_secret=app.config['SYSTEM_CLIENT_SECRET'],
        scope=app.config['SYSTEM_CLIENT_SCOPE'],
    )


@login_manager.user_loader
def load_user(user_id):
    return Session.get(User, user_id)
