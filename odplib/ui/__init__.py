from pathlib import Path

import redis
from flask import Flask
from flask_login import LoginManager

from odplib.client.system import ODPSystemClient
from odplib.client.ui import ODPUIClient
from odplib.config import config
from odplib.localuser import LocalUser

STATIC_DIR = Path(__file__).parent / 'static'
TEMPLATE_DIR = Path(__file__).parent / 'templates'

login_manager = LoginManager()

odp_ui_client: ODPUIClient
odp_system_client: ODPSystemClient


def init_app(app: Flask):
    from . import api, db, forms, templates

    global odp_ui_client
    odp_ui_client = ODPUIClient(
        api_url=app.config['API_URL'],
        hydra_url=config.HYDRA.PUBLIC.URL,
        client_id=app.config['CLIENT_ID'],
        client_secret=app.config['CLIENT_SECRET'],
        scope=app.config['CLIENT_SCOPE'],
        cache=redis.Redis(
            host=config.REDIS.HOST,
            port=config.REDIS.PORT,
            db=config.REDIS.DB,
            decode_responses=True,
        ),
        app=app,
    )

    global odp_system_client
    odp_system_client = ODPSystemClient(
        api_url=app.config['API_URL'],
        hydra_url=config.HYDRA.PUBLIC.URL,
        client_id=app.config['SYSTEM_CLIENT_ID'],
        client_secret=app.config['SYSTEM_CLIENT_SECRET'],
        scope=app.config['SYSTEM_CLIENT_SCOPE'],
    )

    api.init_app(app)
    db.init_app(app)
    forms.init_app(app)
    templates.init_app(app)
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = odp_system_client.get(f'/user/{user_id}')
    return LocalUser(**user)
