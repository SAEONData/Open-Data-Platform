from flask import Flask

from odp.admin import db, views
from odp.config import config


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': config.ODP.ADMIN.UI.FLASK_KEY,
        'FLASK_ADMIN_SWATCH': config.ODP.ADMIN.UI.THEME,
    })

    db.init_app(app)
    views.init_app(app)

    return app
