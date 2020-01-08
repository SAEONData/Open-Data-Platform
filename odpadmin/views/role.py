from odpaccounts.db import session as db_session
from odpaccounts.models.scope import Scope

from .admin import SysAdminModelView, CodeField


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
