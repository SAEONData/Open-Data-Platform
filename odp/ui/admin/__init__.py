from pathlib import Path

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.middleware.proxy_fix import ProxyFix

import odplib.ui
from odp import ODPScope
from odplib.config import config
from odp.lib.hydra import HydraScope
from odp.ui.admin import forms, views


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.ODP.UI.ADMIN.FLASK_KEY,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='Lax',
        CLIENT_ID=config.ODP.UI.ADMIN.CLIENT_ID,
        CLIENT_SECRET=config.ODP.UI.ADMIN.CLIENT_SECRET,
        CLIENT_SCOPE=[HydraScope.OPENID, HydraScope.OFFLINE_ACCESS] + [s.value for s in ODPScope],
        SYSTEM_CLIENT_ID=config.ODP.CLI.ADMIN.CLIENT_ID,
        SYSTEM_CLIENT_SECRET=config.ODP.CLI.ADMIN.CLIENT_SECRET,
        SYSTEM_CLIENT_SCOPE=[s.value for s in ODPScope],
        API_URL=config.ODP.UI.API_URL,
    )

    ui_dir = Path(__file__).parent.parent
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(ui_dir / 'admin' / 'templates'),
        FileSystemLoader(odplib.ui.TEMPLATE_DIR),
    ])
    app.static_folder = odplib.ui.STATIC_DIR

    odplib.ui.init_app(app)
    views.init_app(app)

    # trust the X-Forwarded-* headers set by the proxy server
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_prefix=1)

    return app
