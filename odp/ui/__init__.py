from flask import Flask

from odp import ODPScope
from odp.config import config
from odp.ui import db, auth, views, forms


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

    db.init_app(app)
    auth.init_app(app)
    views.init_app(app)
    forms.init_app(app)

    return app
