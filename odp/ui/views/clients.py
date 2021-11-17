from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize
from odp.ui.forms import ClientForm
from odp.ui.views import utils

bp = Blueprint('clients', __name__)


@bp.route('/')
@authorize(ODPScope.CLIENT_ADMIN, ODPScope.CLIENT_READ)
@api.wrapper
def index():
    clients = api.get('/client/')
    return render_template('client_list.html', clients=clients)


@bp.route('/<id>')
@authorize(ODPScope.CLIENT_ADMIN, ODPScope.CLIENT_READ)
@api.wrapper
def view(id):
    client = api.get(f'/client/{id}')
    return render_template('client_view.html', client=client)


@bp.route('/new', methods=('GET', 'POST'))
@authorize(ODPScope.CLIENT_ADMIN)
@api.wrapper
def create():
    form = ClientForm(request.form)
    utils.populate_provider_choices(form.provider_id, include_none=True)
    utils.populate_scope_choices(form.scope_ids)

    if request.method == 'POST' and form.validate():
        api.post('/client/', dict(
            id=(id := form.id.data),
            name=form.name.data,
            provider_id=form.provider_id.data or None,
            scope_ids=form.scope_ids.data,
        ))
        flash(f'Client {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('client_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@authorize(ODPScope.CLIENT_ADMIN)
@api.wrapper
def edit(id):
    client = api.get(f'/client/{id}')

    # separate get/post form instantiation to resolve
    # ambiguity of missing vs empty multiselect field
    if request.method == 'POST':
        form = ClientForm(request.form)
    else:
        form = ClientForm(data=client)

    utils.populate_provider_choices(form.provider_id, include_none=True)
    utils.populate_scope_choices(form.scope_ids)

    if request.method == 'POST' and form.validate():
        api.put('/client/', dict(
            id=id,
            name=form.name.data,
            provider_id=form.provider_id.data or None,
            scope_ids=form.scope_ids.data,
        ))
        flash(f'Client {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('client_edit.html', client=client, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@authorize(ODPScope.CLIENT_ADMIN)
@api.wrapper
def delete(id):
    api.delete(f'/client/{id}')
    flash(f'Client {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
