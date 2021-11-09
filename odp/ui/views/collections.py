from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize
from odp.ui.forms import CollectionForm

bp = Blueprint('collections', __name__)


@bp.route('/')
@authorize(ODPScope.COLLECTION_READ)
@api.wrapper
def index():
    collections = api.get('/collection/')
    return render_template('collection_list.html', collections=collections)


@bp.route('/<id>')
@authorize(ODPScope.COLLECTION_READ)
@api.wrapper
def view(id):
    collection = api.get(f'/collection/{id}')
    return render_template('collection_view.html', collection=collection)


@bp.route('/new', methods=('GET', 'POST'))
@authorize(ODPScope.COLLECTION_ADMIN)
@api.wrapper
def create():
    providers = api.get('/provider/', sort='name')

    form = CollectionForm(request.form)
    form.provider_id.choices = [
        (provider['id'], provider['name'])
        for provider in providers
    ]

    if request.method == 'POST' and form.validate():
        api.post('/collection/', dict(
            id=(id := form.id.data),
            name=form.name.data,
            provider_id=form.provider_id.data,
        ))
        flash(f'Collection {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('collection_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@authorize(ODPScope.COLLECTION_ADMIN)
@api.wrapper
def edit(id):
    collection = api.get(f'/collection/{id}')
    providers = api.get('/provider/', sort='name')

    form = CollectionForm(request.form, data=collection)
    form.provider_id.choices = [
        (provider['id'], provider['name'])
        for provider in providers
    ]

    if request.method == 'POST' and form.validate():
        api.put('/collection/', dict(
            id=id,
            name=form.name.data,
            provider_id=form.provider_id.data,
        ))
        flash(f'Collection {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('collection_edit.html', collection=collection, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@authorize(ODPScope.COLLECTION_ADMIN)
@api.wrapper
def delete(id):
    api.delete(f'/collection/{id}')
    flash(f'Collection {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
