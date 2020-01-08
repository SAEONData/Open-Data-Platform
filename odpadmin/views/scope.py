from odpaccounts.db import session as db_session
from odpaccounts.models.role import Role

from .admin import SysAdminModelView


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
