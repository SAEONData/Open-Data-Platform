from odpaccounts.db import session as db_session
from odpaccounts.models.institution import Institution
from odpaccounts.models.institution_registry import InstitutionRegistry
from odpaccounts.models.user import User

from .base import AdminModelView, CodeField


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
