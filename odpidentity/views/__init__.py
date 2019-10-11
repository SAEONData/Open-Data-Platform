from flask_login import LoginManager
from flask_admin import Admin

from ..models import db
from ..models.user import User
from ..models.role import Role
from ..models.member import Member
from ..models.scope import Scope
from ..models.institution import Institution
from ..models.institution_registry import InstitutionRegistry

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

    # set up admin views
    home = admin.AdminHomeView()
    users = admin.UserModelView(
        User, db.session,
        name='Users',
        endpoint='users',
    )
    privileges = admin.MemberModelView(
        Member, db.session,
        name='Privileges',
        endpoint='privileges',
    )
    roles = admin.RoleModelView(
        Role, db.session,
        name='Roles',
        endpoint='roles',
        category='System Configuration',
    )
    scopes = admin.ScopeModelView(
        Scope, db.session,
        name='Scopes',
        endpoint='scopes',
        category='System Configuration',
    )
    institutions = admin.InstitutionModelView(
        Institution, db.session,
        name='Institutions',
        endpoint='institutions',
    )
    institution_registries = admin.InstitutionRegistryModelView(
        InstitutionRegistry, db.session,
        name='Institution Registries',
        endpoint='registries',
        category='System Configuration',
    )

    admin_views = Admin(app, name='ODP Admin', index_view=home, base_template='admin_base.html')
    admin_views.add_views(
        institutions,
        users,
        privileges,
        roles,
        scopes,
        institution_registries,
    )
