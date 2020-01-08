from flask import request, flash, redirect
from flask_admin import expose
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_login import current_user

from odpaccounts.db import session as db_session
from odpaccounts.models.institution import Institution
from odpaccounts.models.user import User

from .base import AdminModelView


class UserModelView(AdminModelView):
    """
    User model view.
    """
    can_create = False  # users may only be created via signup
    action_disallowed_list = ['delete']  # disallow deletion of multiple users at once

    column_list = ['id', 'email', 'active', 'superuser', 'confirmed_at', 'institutions']
    column_default_sort = 'email'
    column_formatters = {
        'institutions': lambda vw, ctx, model, prop: ', '.join(sorted([i.name for i in model.institutions]))
    }

    form_columns = ['email', 'active', 'institutions']
    form_args = {
        'institutions': dict(
            get_label='name',
            query_factory=lambda: db_session.query(Institution).order_by('name'),
        )
    }
    edit_template = 'user_edit.html'

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        id = get_mdict_item_or_list(request.args, 'id')
        if id is not None:
            user = db_session.query(User).get(id)
            if user and user.superuser and not current_user.superuser:
                flash("Only superusers may perform this action.")
                return redirect(get_redirect_target())
        return super().edit_view()

    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        id = request.form.get('id')
        if id is not None:
            user = db_session.query(User).get(id)
            if user and user.superuser and not current_user.superuser:
                flash("Only superusers may perform this action.")
                return redirect(get_redirect_target())
        return super().delete_view()
