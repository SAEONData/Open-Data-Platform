from pathlib import Path

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader

from odp import ODPScope
from odp.config import config
from odp.ui import db, auth
from odp.ui.admin import forms, views


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.ODP.UI.FLASK_KEY,
        CLIENT_ID=config.ODP.UI.CLIENT_ID,
        CLIENT_SECRET=config.ODP.UI.CLIENT_SECRET,
        CLIENT_SCOPE=['openid', 'offline'] + [s.value for s in ODPScope],
        API_URL=config.ODP.UI.API_URL,
    )

    ui_dir = Path(__file__).parent.parent
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(ui_dir / 'admin' / 'templates'),
        FileSystemLoader(ui_dir / 'templates'),
    ])
    app.static_folder = ui_dir / 'static'

    db.init_app(app)
    auth.init_app(app)
    views.init_app(app)
    forms.init_app(app)

    return app
