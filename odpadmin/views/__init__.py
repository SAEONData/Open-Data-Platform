from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView

from odpaccounts.db import session as db_session
from odpaccounts.models.user import User
from odpaccounts.models.role import Role
from odpaccounts.models.member import Member
from odpaccounts.models.scope import Scope
from odpaccounts.models.institution import Institution
from odpaccounts.models.institution_registry import InstitutionRegistry

login_manager = LoginManager()
login_manager.login_view = 'oauth2.login'


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)


def init_app(app):
    login_manager.init_app(app)

    from . import hydra_oauth2, user, member, institution, institution_registry, role, scope
    app.register_blueprint(hydra_oauth2.bp, url_prefix='/oauth2')

    home = AdminIndexView(
        url='/',
    )
    users = user.UserModelView(
        User, db_session,
        name='Users',
        endpoint='users',
    )
    privileges = member.MemberModelView(
        Member, db_session,
        name='Privileges',
        endpoint='privileges',
    )
    institutions = institution.InstitutionModelView(
        Institution, db_session,
        name='Institutions',
        endpoint='institutions',
    )
    roles = role.RoleModelView(
        Role, db_session,
        name='Roles',
        category='System Configuration',
        endpoint='roles',
    )
    scopes = scope.ScopeModelView(
        Scope, db_session,
        name='Scopes',
        category='System Configuration',
        endpoint='scopes',
    )
    institution_registries = institution_registry.InstitutionRegistryModelView(
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
