from flask import Flask
from flask_bootstrap import Bootstrap
from werkzeug.middleware.proxy_fix import ProxyFix

from odp.config import config
from odp.identity import db, mail, views, google_oauth2


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': config.ODP.IDENTITY.FLASK_KEY,
        'MAIL_SERVER': config.ODP.MAIL.HOST,
        'MAIL_PORT': config.ODP.MAIL.PORT,
        'MAIL_USE_TLS': config.ODP.MAIL.TLS,
        'MAIL_USERNAME': config.ODP.MAIL.USERNAME,
        'MAIL_PASSWORD': config.ODP.MAIL.PASSWORD,
        'BOOTSTRAP_SERVE_LOCAL': True,
        'BOOTSTRAP_BOOTSWATCH_THEME': 'spacelab',
        'BOOTSTRAP_BTN_SIZE': 'block',
    })

    db.init_app(app)
    views.init_app(app)
    mail.init_app(app)
    google_oauth2.init_app(app)
    Bootstrap(app)

    # trust the X-Forwarded-* headers set by the proxy server
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_prefix=1)

    return app
