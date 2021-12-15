from flask import Flask

from odp.ui.dap.views import session
from odp.ui.views import hydra, home


def init_app(app: Flask):
    app.register_blueprint(home.bp)
    app.register_blueprint(hydra.bp, url_prefix='/oauth2')
    app.register_blueprint(session.bp, url_prefix='/session')
