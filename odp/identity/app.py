from flask import Flask
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
    })

    db.init_app(app)
    views.init_app(app)
    mail.init_app(app)
    google_oauth2.init_app(app)

    # trust the X-Forwarded-* headers set by the proxy server
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_prefix=1)

    return app
