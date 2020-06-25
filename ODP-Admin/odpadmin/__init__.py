from flask import Flask


def create_app(config=None):
    """
    Flask application factory.
    :param config: config dict or filename
    :return: Flask app instance
    """
    from . import models, views, cli
    from .config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    if config is not None:
        if isinstance(config, dict):
            app.config.from_mapping(config)
        else:
            app.config.from_pyfile(config, silent=True)

    models.init_app(app)
    views.init_app(app)
    cli.init_app(app)

    return app
