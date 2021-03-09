from odp.admin.views.base import AdminModelView, KeyField
from odp.db.models import Institution, User, Domain


class InstitutionModelView(AdminModelView):
    """
    Institution model view.
    """
    column_list = ['name', 'key', 'domains', 'parent']
    column_default_sort = 'name'
    column_labels = {
        'users': 'Members',
    }
    column_formatters = {
        'parent': lambda vw, ctx, model, prop: model.parent.name if model.parent else None,
        'domains': lambda vw, ctx, model, prop: ', '.join(sorted([d.name for d in model.domains])),
    }

    form_columns = ['parent', 'name', 'key', 'domains', 'users']
    form_overrides = {
        'key': KeyField
    }
    form_args = {
        'parent': dict(
            get_label='name',
            query_factory=lambda: Institution.query.order_by('name'),
        ),
        'users': dict(
            get_label='email',
            query_factory=lambda: User.query.order_by('email'),
        ),
    }
    inline_models = (Domain,)
    create_template = 'institution_create.html'
    edit_template = 'institution_edit.html'
