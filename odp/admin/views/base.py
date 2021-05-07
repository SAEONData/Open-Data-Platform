import re
from enum import Enum

from flask import flash, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import get_redirect_target
from flask_login import current_user
from wtforms import StringField

from odp.api.models.auth import Role as RoleEnum, Scope as ScopeEnum
from odp.config import config
from odp.db import session
from odp.db.models import Institution, UserPrivilege, Role, Scope


class KeyField(StringField):
    """
    Provides special validation behaviour for 'key' attributes on models. The model
    must have a 'name' attribute.

    If a value is not provided on the create/edit form, then key is generated from name,
    by lowercasing and converting any sequence of non-letter/digit chars to a hyphen.
    """
    def __init__(self, **kwargs):
        kwargs['description'] = "Leave blank to auto-generate a Key based on Name."
        super().__init__(render_kw=dict(required=False), **kwargs)

    def pre_validate(self, form):
        self.data = self.data.strip()
        if not self.data:
            key = re.sub(r'[^a-z0-9]+', '-', form.name.data.lower()).strip('-')
            self.data = key
            self.raw_data = [key]


class AccessLevel(int, Enum):
    NONE = 0
    VIEW = 1
    MANAGE = 2
    ADMIN = 3


class AdminModelView(ModelView):
    """
    Base view for all data models.
    """
    list_template = 'admin_model_list.html'
    create_template = 'admin_model_create.html'
    edit_template = 'admin_model_edit.html'
    details_template = 'admin_model_details.html'

    # minimum access level required to see this view
    read_access_level = AccessLevel.VIEW

    # minimum access level required to make changes in this view
    write_access_level = AccessLevel.MANAGE

    def is_accessible(self):
        """Whether to allow view access."""
        return self.user_access_level() >= self.read_access_level

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """Whether to allow create access."""
        if self.user_access_level() < self.write_access_level:
            return self.redirect_no_perms()

        return super().create_view()

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """Whether to allow edit access."""
        if self.user_access_level() < self.write_access_level:
            return self.redirect_no_perms()

        return super().edit_view()

    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """Whether to allow delete access."""
        if self.user_access_level() < self.write_access_level:
            return self.redirect_no_perms()

        return super().delete_view()

    @expose('/action/', methods=('POST',))
    def action_view(self):
        """Whether to allow any other kind of action (including bulk delete)."""
        if self.user_access_level() < self.write_access_level:
            return self.redirect_no_perms()

        return super().action_view()

    @staticmethod
    def user_access_level() -> AccessLevel:
        """Return the user's access level with respect to this application."""
        if not current_user.is_authenticated:
            return AccessLevel.NONE

        # A user gains read access if they have any user_privilege records
        # referencing both the admin institution and the admin scope.
        # The associated role(s) then determine whether - and what level of -
        # write access is allowed.
        roles = [role for (role,) in
                 (session.query(Role.key)
                  .join(UserPrivilege, UserPrivilege.role_id == Role.id)
                  .join(Institution, UserPrivilege.institution_id == Institution.id)
                  .join(Scope, UserPrivilege.scope_id == Scope.id)
                  .filter(UserPrivilege.user_id == current_user.id)
                  .filter(Institution.key == config.ODP.ADMIN.INSTITUTION)
                  .filter(Scope.key == ScopeEnum.ADMIN)
                  .all())]

        if RoleEnum.ADMIN in roles:
            return AccessLevel.ADMIN
        elif RoleEnum.MANAGER in roles:
            return AccessLevel.MANAGE
        elif roles:
            return AccessLevel.VIEW
        else:
            return AccessLevel.NONE

    @staticmethod
    def redirect_no_perms():
        flash("You do not have permission to perform this action.")
        return redirect(get_redirect_target())


class SysAdminModelView(AdminModelView):
    """
    Base view for system config models. Only modifiable by admins.
    """
    write_access_level = AccessLevel.ADMIN
