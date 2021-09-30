from flask import Flask

from odp.app import db, views
from odp.config import config


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': config.ODP.APP.FLASK_KEY,
    })

    db.init_app(app)
    views.init_app(app)

    return app
