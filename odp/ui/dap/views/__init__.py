from flask import Flask

from odp.ui.views import hydra, home


def init_app(app: Flask):
    app.register_blueprint(home.bp)
    app.register_blueprint(hydra.bp, url_prefix='/oauth2')
