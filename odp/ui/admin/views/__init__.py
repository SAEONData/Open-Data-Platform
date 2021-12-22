import json
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask

from odp.ui.admin.views import (
    home,
    projects,
    providers,
    collections,
    records,
    users,
    roles,
    tags,
    schemas,
    clients,
    catalogues,
)
from odp.ui.views import hydra


def init_app(app: Flask):
    app.register_blueprint(home.bp)
    app.register_blueprint(hydra.bp, url_prefix='/oauth2')
    app.register_blueprint(projects.bp, url_prefix='/projects')
    app.register_blueprint(providers.bp, url_prefix='/providers')
    app.register_blueprint(collections.bp, url_prefix='/collections')
    app.register_blueprint(records.bp, url_prefix='/records')
    app.register_blueprint(users.bp, url_prefix='/users')
    app.register_blueprint(roles.bp, url_prefix='/roles')
    app.register_blueprint(tags.bp, url_prefix='/tags')
    app.register_blueprint(schemas.bp, url_prefix='/schemas')
    app.register_blueprint(clients.bp, url_prefix='/clients')
    app.register_blueprint(catalogues.bp, url_prefix='/catalogues')

    @app.template_filter()
    def format_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    @app.template_filter()
    def timestamp(value):
        dt = datetime.fromisoformat(value).astimezone(ZoneInfo('Africa/Johannesburg'))
        return dt.strftime('%d %b %Y, %H:%M %Z')