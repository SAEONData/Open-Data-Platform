from flask import flash
from flask_admin.helpers import is_form_submitted

from odp.admin.views.base import AdminModelView, AccessLevel
from odp.api.models.auth import Role as RoleEnum
from odp.db.models import Capability, Role, Scope


class MemberModelView(AdminModelView):
    """
    Member model view. Used for assigning capabilities to members -
    effectively creating/deleting user_privilege records.
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
            query_factory=lambda: Capability.query.join(Scope).join(Role).order_by(Scope.key, Role.name),
        )
    }
    edit_template = 'member_edit.html'

    def validate_form(self, form):
        """Make sure that only an admin may grant any kind
        of admin rights to anyone.

        Someone with management-level access can still, however,
        delete admin users or revoke their admin rights.
        """
        if is_form_submitted():
            if self.user_access_level() < AccessLevel.ADMIN:
                if any(
                        capability for capability in form.data['capabilities']
                        if capability.role.key == RoleEnum.ADMIN
                ):
                    flash("You do not have permission to grant admin rights.")
                    return False

        return super().validate_form(form)
