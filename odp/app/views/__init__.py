from flask_login import LoginManager

from odp.app.views import (
    hydra,
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
    scopes,
    catalogues,
    datastores,
)
from odp.db import Session
from odp.db.models import User

login_manager = LoginManager()
login_manager.login_view = 'hydra.login'


@login_manager.user_loader
def load_user(user_id):
    return Session.get(User, user_id)


def init_app(app):
    login_manager.init_app(app)
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
    app.register_blueprint(scopes.bp, url_prefix='/scopes')
    app.register_blueprint(catalogues.bp, url_prefix='/catalogues')
    app.register_blueprint(datastores.bp, url_prefix='/datastores')
