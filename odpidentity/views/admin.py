from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from ..models import db
from ..models.user import User
from ..models.role import Role
from ..models.scope import Scope
from ..models.institution import Institution
from ..models.institution_registry import InstitutionRegistry


class AdminHomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class UserModelView(AdminModelView):
    column_exclude_list = ['password']
    form_excluded_columns = ['password']


class RoleModelView(AdminModelView):
    pass


class ScopeModelView(AdminModelView):
    pass


class InstitutionModelView(AdminModelView):
    pass


class InstitutionRegistryModelView(AdminModelView):
    pass


home = AdminHomeView()

users = UserModelView(
    User, db.session,
    name='Users',
    endpoint='users',
)
roles = RoleModelView(
    Role, db.session,
    name='Roles',
    endpoint='roles',
)
scopes = ScopeModelView(
    Scope, db.session,
    name='Scopes',
    endpoint='scopes',
)
institutions = InstitutionModelView(
    Institution, db.session,
    name='Institutions',
    category='Institutions',
    endpoint='institutions',
)
institution_registries = InstitutionRegistryModelView(
    InstitutionRegistry, db.session,
    name='Institution Registries',
    category='Institutions',
    endpoint='institution_registries',
)
