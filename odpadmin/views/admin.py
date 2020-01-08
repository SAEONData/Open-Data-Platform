import re

from flask import current_app, flash, redirect, request
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_login import current_user
from wtforms import StringField

from odpaccounts.db import session as db_session
from odpaccounts.models.user import User
from odpaccounts.models.role import Role
from odpaccounts.models.capability import Capability
from odpaccounts.models.scope import Scope
from odpaccounts.models.institution import Institution
from odpaccounts.models.institution_registry import InstitutionRegistry
from odpaccounts.models.privilege import Privilege


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


class AdminModelView(ModelView):
    """
    Base view for all data models.
    """
    list_template = 'admin_model_list.html'
    create_template = 'admin_model_create.html'
    edit_template = 'admin_model_edit.html'
    details_template = 'admin_model_details.html'

    def is_accessible(self):
        if not current_user.is_authenticated:
            return False

        if current_user.superuser:
            return True

        # TODO: cache the result of this query; it's called repeatedly
        admin_privilege = db_session.query(Privilege).filter_by(user_id=current_user.id) \
            .join(Institution, Privilege.institution_id == Institution.id).filter_by(code=current_app.config['ADMIN_INSTITUTION']) \
            .join(Role, Privilege.role_id == Role.id).filter_by(code=current_app.config['ADMIN_ROLE']) \
            .join(Scope, Privilege.scope_id == Scope.id).filter_by(code=current_app.config['ADMIN_SCOPE']) \
            .one_or_none()
        return admin_privilege is not None


class SysAdminModelView(AdminModelView):
    """
    Base view for system config models. Only modifiable by superusers.
    """
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        if not current_user.superuser:
            flash("Only superusers may perform this action.")
            return redirect(get_redirect_target())
        return super().create_view()

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if not current_user.superuser:
            flash("Only superusers may perform this action.")
            return redirect(get_redirect_target())
        return super().edit_view()

    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        if not current_user.superuser:
            flash("Only superusers may perform this action.")
            return redirect(get_redirect_target())
        return super().delete_view()

    @expose('/action/', methods=('POST',))
    def action_view(self):
        if not current_user.superuser:
            flash("Only superusers may perform this action.")
            return redirect(get_redirect_target())
        return super().action_view()


class UserModelView(AdminModelView):
    """
    User model view.
    """
    can_create = False  # users may only be created via signup
    action_disallowed_list = ['delete']  # disallow deletion of multiple users at once

    column_list = ['id', 'email', 'active', 'superuser', 'confirmed_at', 'institutions']
    column_default_sort = 'email'
    column_formatters = {
        'institutions': lambda vw, ctx, model, prop: ', '.join(sorted([i.name for i in model.institutions]))
    }

    form_columns = ['email', 'active', 'institutions']
    form_args = {
        'institutions': dict(
            get_label='name',
            query_factory=lambda: db_session.query(Institution).order_by('name'),
        )
    }
    edit_template = 'user_edit.html'

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        id = get_mdict_item_or_list(request.args, 'id')
        if id is not None:
            user = db_session.query(User).get(id)
            if user and user.superuser and not current_user.superuser:
                flash("Only superusers may perform this action.")
                return redirect(get_redirect_target())
        return super().edit_view()

    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        id = request.form.get('id')
        if id is not None:
            user = db_session.query(User).get(id)
            if user and user.superuser and not current_user.superuser:
                flash("Only superusers may perform this action.")
                return redirect(get_redirect_target())
        return super().delete_view()


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
            query_factory=lambda: db_session.query(Capability).join(Scope).join(Role).order_by(Scope.code, Role.name),
        )
    }
    edit_template = 'member_edit.html'


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
            query_factory=lambda: db_session.query(InstitutionRegistry).order_by('name'),
        ),
        'parent': dict(
            get_label='name',
            query_factory=lambda: db_session.query(Institution).order_by('name'),
        ),
        'users': dict(
            get_label='email',
            query_factory=lambda: db_session.query(User).order_by('email'),
        ),
    }
    create_template = 'institution_create.html'
    edit_template = 'institution_edit.html'


class RoleModelView(SysAdminModelView):
    """
    Role model view.
    """
    column_list = ['name', 'code', 'scopes']
    column_default_sort = 'name'
    column_formatters = {
        'scopes': lambda vw, ctx, model, prop: ', '.join(sorted([s.code for s in model.scopes]))
    }

    form_columns = ['name', 'code', 'scopes']
    form_overrides = {
        'code': CodeField
    }
    form_args = {
        'scopes': dict(
            get_label='code',
            query_factory=lambda: db_session.query(Scope).order_by('code'),
        )
    }
    create_template = 'role_create.html'
    edit_template = 'role_edit.html'


class ScopeModelView(SysAdminModelView):
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
            query_factory=lambda: db_session.query(Role).order_by('name'),
        )
    }
    create_template = 'scope_create.html'
    edit_template = 'scope_edit.html'


class InstitutionRegistryModelView(SysAdminModelView):
    """
    InstitutionRegistry model view.
    """
    column_list = ['name', 'code']
    column_default_sort = 'name'

    form_columns = ['name', 'code']
    form_overrides = {
        'code': CodeField
    }
