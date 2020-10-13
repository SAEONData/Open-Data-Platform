import re

from flask import flash, redirect
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import get_redirect_target
from flask_login import current_user
from wtforms import StringField

from odp.config import config
from odp.db import session as db_session
from odp.db.models.institution import Institution
from odp.db.models.user_privilege import UserPrivilege
from odp.db.models.role import Role
from odp.db.models.scope import Scope


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
        admin_privilege = db_session.query(UserPrivilege).filter_by(user_id=current_user.id) \
            .join(Institution, UserPrivilege.institution_id == Institution.id).filter_by(key=config.ODP.ADMIN.INSTITUTION) \
            .join(Role, UserPrivilege.role_id == Role.id).filter_by(key=config.ODP.ADMIN.ROLE) \
            .join(Scope, UserPrivilege.scope_id == Scope.id).filter_by(key=config.ODP.ADMIN.SCOPE) \
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
