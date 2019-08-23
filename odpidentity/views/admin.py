from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from ..models import db
from ..models.user import User
from ..models.role import Role
from ..models.scope import Scope
from ..models.institution import Institution
from ..models.institution_registry import InstitutionRegistry
from ..lib.utils import make_object_name


class AdminHomeView(AdminIndexView):
    """
    Admin UI home page view.
    """
    def is_accessible(self):
        return current_user.is_authenticated


class AdminModelView(ModelView):
    """
    Base view for all data models.
    """
    def is_accessible(self):
        return current_user.is_authenticated


class UserModelView(AdminModelView):
    """
    User model view.
    """
    column_exclude_list = ['password']
    form_excluded_columns = ['password']


class StaticDataModelView(AdminModelView):
    """
    Base view for static data models.
    """
    column_default_sort = 'name'
    form_excluded_columns = ['name']
    form_args = {
        'title': {
            'filters': [lambda s: s.strip() if s else s],
        }
    }

    def on_model_change(self, form, model, is_created):
        # generate the name field from the title
        if is_created:
            model.name = make_object_name(model.title)


class RoleModelView(StaticDataModelView):
    """
    Role model view.
    """
    form_excluded_columns = ['name', 'scopes']


class ScopeModelView(StaticDataModelView):
    """
    Scope model view.
    """
    form_excluded_columns = ['name', 'roles']


class InstitutionModelView(StaticDataModelView):
    """
    Institution model view.
    """
    form_excluded_columns = ['name', 'children', 'users']


class InstitutionRegistryModelView(StaticDataModelView):
    """
    InstitutionRegistry model view.
    """
    form_excluded_columns = ['name', 'institutions']


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
