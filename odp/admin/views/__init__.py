from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager

from odp.admin.views import hydra_oauth2, user, member, institution, role, scope
from odp.db import session as db_session
from odp.db.models import Institution, Member, Role, Scope, User

login_manager = LoginManager()
login_manager.login_view = 'hydra.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def init_app(app):
    login_manager.init_app(app)
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

    admin_views = Admin(app, name='ODP Admin', index_view=home, base_template='admin_base.html')
    admin_views.add_views(
        institutions,
        users,
        privileges,
        roles,
        scopes,
    )
