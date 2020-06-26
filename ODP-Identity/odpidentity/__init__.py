from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask.helpers import get_env
from werkzeug.middleware.proxy_fix import ProxyFix

from hydra import HydraAdminClient
from odpaccounts.db import session as db_session
from odpaccounts.models.user import User


login_manager = LoginManager()
login_manager.login_view = 'odpidentity.login'

mail = Mail()

hydra_admin = HydraAdminClient('')


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)


def create_app(config=None):
    """
    Flask application factory.

    :param config: config dict or filename
    :return: Flask app instance
    """
    from . import models, views
    from .config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    if config is not None:
        if isinstance(config, dict):
            app.config.from_mapping(config)
        else:
            app.config.from_pyfile(config, silent=True)

    models.init_app(app)
    views.init_app(app)

    login_manager.init_app(app)
    mail.init_app(app)

    hydra_admin.server_url = app.config['HYDRA_ADMIN_URL']
    hydra_admin.remember_login_for = app.config['HYDRA_LOGIN_EXPIRY']
    hydra_admin.verify_tls = get_env() != 'development'

    # trust the X-Forwarded-* headers set by the proxy server
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_prefix=1)

    return app
