from flask_login import LoginManager
from flask_admin import Admin

from ..models.user import User

login_manager = LoginManager()
login_manager.login_view = 'hydra.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def init_app(app):
    login_manager.init_app(app)

    from . import home, user, hydra_client, hydra_auth, admin
    app.register_blueprint(home.bp, url_prefix='/')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(hydra_client.bp, url_prefix='/user')
    app.register_blueprint(hydra_auth.bp, url_prefix='/auth')

    admin_views = Admin(app, name='ODP Admin', index_view=admin.home, base_template='admin_base.html')
    admin_views.add_views(
        admin.users,
        admin.members,
        admin.roles,
        admin.scopes,
        admin.institutions,
        admin.institution_registries,
    )
