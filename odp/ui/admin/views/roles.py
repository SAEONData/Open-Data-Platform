from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp import ODPScope
from odp.ui import api
from odp.ui.admin.forms import RoleForm
from odp.ui.admin.views import utils

bp = Blueprint('roles', __name__)


@bp.route('/')
@api.client(ODPScope.ROLE_READ)
def index():
    page = request.args.get('page', 1)
    roles = api.get(f'/role/?page={page}')
    return render_template('role_list.html', roles=roles)


@bp.route('/<id>')
@api.client(ODPScope.ROLE_READ)
def view(id):
    role = api.get(f'/role/{id}')
    return render_template('role_view.html', role=role)


@bp.route('/new', methods=('GET', 'POST'))
@api.client(ODPScope.ROLE_ADMIN)
def create():
    form = RoleForm(request.form)
    utils.populate_provider_choices(form.provider_id, include_none=True)
    utils.populate_scope_choices(form.scope_ids, ('odp', 'client'))

    if request.method == 'POST' and form.validate():
        try:
            api.post('/role/', dict(
                id=(id := form.id.data),
                provider_id=form.provider_id.data or None,
                scope_ids=form.scope_ids.data,
            ))
            flash(f'Role {id} has been created.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('role_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.ROLE_ADMIN)
def edit(id):
    role = api.get(f'/role/{id}')

    # separate get/post form instantiation to resolve
    # ambiguity of missing vs empty multiselect field
    if request.method == 'POST':
        form = RoleForm(request.form)
    else:
        form = RoleForm(data=role)

    utils.populate_provider_choices(form.provider_id, include_none=True)
    utils.populate_scope_choices(form.scope_ids, ('odp', 'client'))

    if request.method == 'POST' and form.validate():
        try:
            api.put('/role/', dict(
                id=id,
                provider_id=form.provider_id.data or None,
                scope_ids=form.scope_ids.data,
            ))
            flash(f'Role {id} has been updated.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('role_edit.html', role=role, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@api.client(ODPScope.ROLE_ADMIN)
def delete(id):
    api.delete(f'/role/{id}')
    flash(f'Role {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
