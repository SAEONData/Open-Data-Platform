from flask import Flask

from odp.config import config


def create_app():
    """
    Flask application factory.
    """
    from . import db, views

    app = Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': config.ODP.ADMIN.UI.FLASK_KEY,
        'FLASK_ADMIN_SWATCH': config.ODP.ADMIN.UI.THEME,
        'HYDRA_PUBLIC_URL': config.HYDRA.PUBLIC.URL,
        'OAUTH2_CLIENT_ID': config.ODP.ADMIN.UI.CLIENT_ID,
        'OAUTH2_CLIENT_SECRET': config.ODP.ADMIN.UI.CLIENT_SECRET,
        'OAUTH2_SCOPES': config.ODP.ADMIN.UI.SCOPE,
    })

    db.init_app(app)
    views.init_app(app)

    return app
