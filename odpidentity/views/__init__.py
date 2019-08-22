from flask_login import LoginManager
from flask_admin import Admin

from ..models.user import User

login_manager = LoginManager()
login_manager.login_view = 'hydra.login'


def init_app(app):
    from . import home, user, hydra_client, hydra_auth, admin
    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(hydra_client.bp, url_prefix='/user')
    app.register_blueprint(hydra_auth.bp, url_prefix='/auth')
    login_manager.init_app(app)
    admin_views = Admin(app, name='ODP Administration', index_view=admin.home)
    admin_views.add_view(admin.users)
    admin_views.add_view(admin.roles)
    admin_views.add_view(admin.scopes)
    admin_views.add_view(admin.institutions)
    admin_views.add_view(admin.institution_registries)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
