from odp.db import session as db_session
from odp.db.models.scope import Scope

from .base import SysAdminModelView, KeyField


class RoleModelView(SysAdminModelView):
    """
    Role model view.
    """
    column_list = ['name', 'key', 'scopes']
    column_default_sort = 'name'
    column_formatters = {
        'scopes': lambda vw, ctx, model, prop: ', '.join(sorted([s.key for s in model.scopes]))
    }

    form_columns = ['name', 'key', 'scopes']
    form_overrides = {
        'key': KeyField
    }
    form_args = {
        'scopes': dict(
            get_label='key',
            query_factory=lambda: db_session.query(Scope).order_by('key'),
        )
    }
    create_template = 'role_create.html'
    edit_template = 'role_edit.html'
