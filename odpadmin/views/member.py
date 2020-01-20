from odpaccounts.db import session as db_session
from odpaccounts.models.capability import Capability
from odpaccounts.models.role import Role
from odpaccounts.models.scope import Scope

from .base import AdminModelView


class MemberModelView(AdminModelView):
    """
    Member model view. Used for assigning capabilities to members -
    effectively creating/deleting privilege records.
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
            query_factory=lambda: db_session.query(Capability).join(Scope).join(Role).order_by(Scope.key, Role.name),
        )
    }
    edit_template = 'member_edit.html'
