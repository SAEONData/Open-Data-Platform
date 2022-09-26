from flask import Flask

from odp.ui.dap.views import home, session
from odplib.ui.views import hydra


def init_app(app: Flask):
    app.register_blueprint(home.bp)
    app.register_blueprint(hydra.bp, url_prefix='/oauth2')
    app.register_blueprint(session.bp, url_prefix='/session')
