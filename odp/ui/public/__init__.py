from pathlib import Path

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader

from odp.config import config
from odp.ui import db, auth
from odp.ui.public import views


def create_app():
    """
    Flask application factory.
    """
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.ODP.UI.PUBLIC.FLASK_KEY,
        CLIENT_ID=config.ODP.UI.PUBLIC.CLIENT_ID,
        CLIENT_SECRET=config.ODP.UI.PUBLIC.CLIENT_SECRET,
        CLIENT_SCOPE=config.ODP.UI.PUBLIC.SCOPE,
    )

    ui_dir = Path(__file__).parent.parent
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(ui_dir / 'public' / 'templates'),
        FileSystemLoader(ui_dir / 'templates'),
    ])
    app.static_folder = ui_dir / 'static'

    db.init_app(app)
    auth.init_app(app)
    views.init_app(app)

    return app
