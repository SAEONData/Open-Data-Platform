from flask import Flask

from odp.config import config
from odp.ui import db, auth, views, forms


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': config.ODP.UI.FLASK_KEY,
    })

    db.init_app(app)
    auth.init_app(app)
    views.init_app(app)
    forms.init_app(app)

    return app
