from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize
from odp.ui.forms import RoleForm

bp = Blueprint('roles', __name__)


@bp.route('/')
@authorize(ODPScope.ROLE_READ)
@api.wrapper
def index():
    roles = api.get('/role/')
    return render_template('role_list.html', roles=roles)


@bp.route('/<id>')
@authorize(ODPScope.ROLE_READ)
@api.wrapper
def view(id):
    role = api.get(f'/role/{id}')
    return render_template('role_view.html', role=role)


@bp.route('/new', methods=('GET', 'POST'))
@authorize(ODPScope.ROLE_ADMIN)
@api.wrapper
def create():
    providers = api.get('/provider/', sort='name')
    scopes = api.get('/scope/')

    form = RoleForm(request.form)
    form.provider_id.choices = [('', '(None)')] + [
        (provider['id'], provider['name'])
        for provider in providers
    ]
    form.scope_ids.choices = [
        (scope['id'], scope['id'])
        for scope in scopes
    ]

    if request.method == 'POST' and form.validate():
        api.post('/role/', dict(
            id=(id := form.id.data),
            provider_id=form.provider_id.data or None,
            scope_ids=form.scope_ids.data,
        ))
        flash(f'Role {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('role_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@authorize(ODPScope.ROLE_ADMIN)
@api.wrapper
def edit(id):
    role = api.get(f'/role/{id}')
    providers = api.get('/provider/', sort='name')
    scopes = api.get('/scope/')

    # separate get/post form instantiation to resolve
    # ambiguity of missing vs empty multiselect field
    if request.method == 'POST':
        form = RoleForm(request.form)
    else:
        form = RoleForm(data=role)

    form.provider_id.choices = [('', '(None)')] + [
        (provider['id'], provider['name'])
        for provider in providers
    ]
    form.scope_ids.choices = [
        (scope['id'], scope['id'])
        for scope in scopes
    ]

    if request.method == 'POST' and form.validate():
        api.put('/role/', dict(
            id=id,
            provider_id=form.provider_id.data or None,
            scope_ids=form.scope_ids.data,
        ))
        flash(f'Role {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('role_edit.html', role=role, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@authorize(ODPScope.ROLE_ADMIN)
@api.wrapper
def delete(id):
    api.delete(f'/role/{id}')
    flash(f'Role {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
