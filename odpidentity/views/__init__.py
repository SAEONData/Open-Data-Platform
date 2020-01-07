from flask_login import LoginManager
from flask_admin import Admin

from ..models import db_session
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
    return db_session.query(User).get(user_id)


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
        User, db_session,
        name='Users',
        endpoint='users',
    )
    privileges = admin.MemberModelView(
        Member, db_session,
        name='Privileges',
        endpoint='privileges',
    )
    institutions = admin.InstitutionModelView(
        Institution, db_session,
        name='Institutions',
        endpoint='institutions',
    )
    roles = admin.RoleModelView(
        Role, db_session,
        name='Roles',
        category='System Configuration',
        endpoint='roles',
    )
    scopes = admin.ScopeModelView(
        Scope, db_session,
        name='Scopes',
        category='System Configuration',
        endpoint='scopes',
    )
    institution_registries = admin.InstitutionRegistryModelView(
        InstitutionRegistry, db_session,
        name='Institution Registries',
        category='System Configuration',
        endpoint='registries',
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
