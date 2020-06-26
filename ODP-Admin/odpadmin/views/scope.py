from odpaccounts.db import session as db_session
from odpaccounts.models.role import Role

from .base import SysAdminModelView


class ScopeModelView(SysAdminModelView):
    """
    Scope model view.
    """
    column_list = ['key', 'description', 'roles']
    column_default_sort = 'key'
    column_formatters = {
        'roles': lambda vw, ctx, model, prop: ', '.join(sorted([r.name for r in model.roles]))
    }

    form_columns = ['key', 'description', 'roles']
    form_args = {
        'key': dict(
            filters=[lambda s: s.strip() if s else s]
        ),
        'roles': dict(
            get_label='name',
            query_factory=lambda: db_session.query(Role).order_by('name'),
        )
    }
    create_template = 'scope_create.html'
    edit_template = 'scope_edit.html'
