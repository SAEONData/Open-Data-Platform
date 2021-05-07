from sqlalchemy import Boolean, String

from odp.admin.views.base import AdminModelView
from odp.db.models import Institution


class UserModelView(AdminModelView):
    """
    User model view.
    """
    can_create = False  # users may only be created via signup
    action_disallowed_list = ['delete']  # disallow deletion of multiple users at once

    column_list = ['id', 'email', 'verified', 'active', 'institutions']
    column_default_sort = 'email'
    column_formatters = {
        'institutions': lambda vw, ctx, model, prop: ', '.join(sorted([i.name for i in model.institutions]))
    }

    form_columns = ['id', 'email', 'active', 'institutions']
    form_args = {
        'institutions': dict(
            get_label='name',
            query_factory=lambda: Institution.query.order_by('name'),
        )
    }
    form_widget_args = {
        'id': dict(
            disabled=True,
            style='color: black; width: 30%',
        ),
        'email': dict(
            disabled=True,
            style='color: black; width: 30%',
        ),
    }
    form_optional_types = (Boolean, String)  # force email field to be non-mandatory
    edit_template = 'user_edit.html'
