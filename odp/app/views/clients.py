from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp.app import api
from odp.app.forms import ClientForm

bp = Blueprint('clients', __name__)


@bp.route('/')
def index():
    clients = api.get('/client/')
    return render_template('client_list.html', clients=clients)


@bp.route('/<id>')
def view(id):
    client = api.get(f'/client/{id}')
    return render_template('client_view.html', client=client)


@bp.route('/new', methods=('GET', 'POST'))
def create():
    form = ClientForm(request.form)

    if request.method == 'POST' and form.validate():
        api.post('/client/', dict(
            id=(id := form.id.data),
            name=form.name.data,
        ))
        flash(f'Client {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('client_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    client = api.get(f'/client/{id}')
    form = ClientForm(request.form, data=client)

    if request.method == 'POST' and form.validate():
        api.put('/client/', dict(
            id=id,
            name=form.name.data,
        ))
        flash(f'Client {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('client_edit.html', client=client, form=form)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    api.delete(f'/client/{id}')
    flash(f'Client {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
