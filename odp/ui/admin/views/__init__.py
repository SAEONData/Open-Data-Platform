from flask import Flask

from odp.ui.admin.views import catalogs, clients, collections, home, providers, records, roles, schemas, tags, users, vocabularies
from odp.ui.views import hydra


def init_app(app: Flask):
    app.register_blueprint(home.bp)
    app.register_blueprint(hydra.bp, url_prefix='/oauth2')
    app.register_blueprint(catalogs.bp, url_prefix='/catalogs')
    app.register_blueprint(clients.bp, url_prefix='/clients')
    app.register_blueprint(collections.bp, url_prefix='/collections')
    app.register_blueprint(providers.bp, url_prefix='/providers')
    app.register_blueprint(records.bp, url_prefix='/records')
    app.register_blueprint(roles.bp, url_prefix='/roles')
    app.register_blueprint(schemas.bp, url_prefix='/schemas')
    app.register_blueprint(tags.bp, url_prefix='/tags')
    app.register_blueprint(users.bp, url_prefix='/users')
    app.register_blueprint(vocabularies.bp, url_prefix='/vocabularies')
