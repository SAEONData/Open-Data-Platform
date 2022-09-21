from pathlib import Path

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.middleware.proxy_fix import ProxyFix

from odp import ODPScope
from odp.config import config
from odp.lib.hydra import HydraScope
from odp.ui import auth, db, templates
from odp.ui.public import forms, views


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.ODP.UI.PUBLIC.FLASK_KEY,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='Lax',
        CLIENT_ID=config.ODP.UI.PUBLIC.CLIENT_ID,
        CLIENT_SECRET=config.ODP.UI.PUBLIC.CLIENT_SECRET,
        CLIENT_SCOPE=[HydraScope.OPENID, HydraScope.OFFLINE_ACCESS, ODPScope.CATALOG_READ],
        API_URL=config.ODP.UI.PUBLIC.API_URL,
    )

    ui_dir = Path(__file__).parent.parent
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(ui_dir / 'public' / 'templates'),
        FileSystemLoader(ui_dir / 'templates'),
    ])
    app.static_folder = ui_dir / 'static'

    db.init_app(app)
    auth.init_app(app)
    templates.init_app(app)
    views.init_app(app)
    forms.init_app(app)

    # trust the X-Forwarded-* headers set by the proxy server
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_prefix=1)

    return app