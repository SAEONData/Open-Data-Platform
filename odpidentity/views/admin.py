import re

from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import StringField

from ..models import db
from ..models.user import User
from ..models.role import Role
from ..models.capability import Capability
from ..models.member import Member
from ..models.scope import Scope
from ..models.institution import Institution
from ..models.institution_registry import InstitutionRegistry


class CodeField(StringField):
    """
    Provides special validation behaviour for 'code' attributes on models. The model
    must have a 'name' attribute.

    If a value is not provided on the create/edit form, then code is generated from name,
    by lowercasing and converting any sequence of non-letter/digit chars to a hyphen.
    """
    def __init__(self, **kwargs):
        kwargs['description'] = "Leave blank to auto-generate a Code based on Name."
        super().__init__(render_kw=dict(required=False), **kwargs)

    def pre_validate(self, form):
        self.data = self.data.strip()
        if not self.data:
            code = re.sub(r'[^a-z0-9]+', '-', form.name.data.lower()).strip('-')
            self.data = code
            self.raw_data = [code]


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
    list_template = 'admin_model_list.html'
    create_template = 'admin_model_create.html'
    edit_template = 'admin_model_edit.html'
    details_template = 'admin_model_details.html'

    def is_accessible(self):
        return current_user.is_authenticated


class UserModelView(AdminModelView):
    """
    User model view.
    """
    can_create = False
    column_list = ['id', 'email', 'active', 'confirmed_at', 'institutions']
    column_default_sort = 'email'
    column_formatters = {
        'institutions': lambda vw, ctx, model, prop: ', '.join(sorted([i.name for i in model.institutions]))
    }
    form_columns = ['email', 'active', 'institutions']
    form_args = {
        'institutions': dict(
            get_label='name',
            query_factory=lambda: Institution.query.order_by('name'),
        )
    }
    edit_template = 'user_edit.html'


class MemberModelView(AdminModelView):
    """
    Member model view. Used for assigning capabilities to members.
    """
    can_create = False
    can_delete = False
    column_list = ['user.email', 'institution.name', 'capabilities']
    column_default_sort = [('user.email', False), ('institution.name', False)]
    column_labels = {
        'user.email': 'User',
        'institution.name': 'Institution',
    }
    column_formatters = {
        'capabilities': lambda vw, ctx, model, prop: ', '.join(sorted([c.label for c in model.capabilities]))
    }
    form_columns = ['capabilities']
    form_args = {
        'capabilities': dict(
            get_label='label',
            query_factory=lambda: db.session.query(Capability).join(Scope).join(Role).order_by(Scope.code, Role.name),
        )
    }
    edit_template = 'member_edit.html'


class ScopeModelView(AdminModelView):
    """
    Scope model view.
    """
    column_list = ['code', 'description', 'roles']
    column_default_sort = 'code'
    column_formatters = {
        'roles': lambda vw, ctx, model, prop: ', '.join(sorted([r.name for r in model.roles]))
    }
    form_columns = ['code', 'description', 'roles']
    form_args = {
        'code': dict(
            filters=[lambda s: s.strip() if s else s]
        ),
        'roles': dict(
            get_label='name',
            query_factory=lambda: Role.query.order_by('name'),
        )
    }
    create_template = 'scope_create.html'
    edit_template = 'scope_edit.html'


class RoleModelView(AdminModelView):
    """
    Role model view.
    """
    column_list = ['name', 'code', 'is_admin', 'scopes']
    column_default_sort = 'name'
    column_formatters = {
        'scopes': lambda vw, ctx, model, prop: ', '.join(sorted([s.code for s in model.scopes]))
    }
    form_columns = ['name', 'code', 'is_admin', 'scopes']
    form_overrides = {
        'code': CodeField
    }
    form_args = {
        'scopes': dict(
            get_label='code',
            query_factory=lambda: Scope.query.order_by('code'),
        )
    }
    create_template = 'role_create.html'
    edit_template = 'role_edit.html'


class InstitutionModelView(AdminModelView):
    """
    Institution model view.
    """
    column_list = ['name', 'code', 'parent', 'registry.name']
    column_default_sort = 'name'
    column_labels = {
        'registry.name': 'Registry',
        'users': 'Members',
    }
    column_formatters = {
        'parent': lambda vw, ctx, model, prop: model.parent.name if model.parent else None
    }
    form_columns = ['registry', 'parent', 'name', 'code', 'users']
    form_overrides = {
        'code': CodeField
    }
    form_args = {
        'registry': dict(
            get_label='name',
            query_factory=lambda: InstitutionRegistry.query.order_by('name'),
        ),
        'parent': dict(
            get_label='name',
            query_factory=lambda: Institution.query.order_by('name'),
        ),
        'users': dict(
            get_label='email',
            query_factory=lambda: User.query.order_by('email'),
        ),
    }
    create_template = 'institution_create.html'
    edit_template = 'institution_edit.html'


class InstitutionRegistryModelView(AdminModelView):
    """
    InstitutionRegistry model view.
    """
    column_list = ['name', 'code']
    column_default_sort = 'name'
    form_columns = ['name', 'code']
    form_overrides = {
        'code': CodeField
    }


home = AdminHomeView()

users = UserModelView(
    User, db.session,
    name='Users',
    category='Users',
    endpoint='users',
)
members = MemberModelView(
    Member, db.session,
    name='User Roles',
    category='Users',
    endpoint='users/roles',
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
    endpoint='institutions/registries',
)
