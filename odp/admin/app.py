from flask import Flask


def create_app(config=None):
    """
    Flask application factory.
    :param config: config dict or filename
    :return: Flask app instance
    """
    from . import views, cli
    from .config import Config
    from odp.db import session

    app = Flask(__name__)
    app.config.from_object(Config)

    if config is not None:
        if isinstance(config, dict):
            app.config.from_mapping(config)
        else:
            app.config.from_pyfile(config, silent=True)

    views.init_app(app)
    cli.init_app(app)

    # ensure that the db session is closed and disposed after each request
    @app.teardown_appcontext
    def discard_session(exc):
        session.remove()

    return app
