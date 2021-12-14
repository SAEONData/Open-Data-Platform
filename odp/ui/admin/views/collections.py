from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp import ODPScope, ODPFlag
from odp.ui import api
from odp.ui.admin.forms import CollectionForm
from odp.ui.admin.views import utils

bp = Blueprint('collections', __name__)


@bp.route('/')
@api.client(ODPScope.COLLECTION_READ)
def index():
    collections = api.get('/collection/')
    return render_template('collection_list.html', collections=collections)


@bp.route('/<id>')
@api.client(ODPScope.COLLECTION_READ)
def view(id):
    collection = api.get(f'/collection/{id}')
    publish_flag = next(
        (flag for flag in collection['flags']
         if flag['flag_id'] == ODPFlag.COLLECTION_PUBLISH),
        None
    )
    return render_template('collection_view.html', collection=collection, publish_flag=publish_flag)


@bp.route('/new', methods=('GET', 'POST'))
@api.client(ODPScope.COLLECTION_ADMIN)
def create():
    form = CollectionForm(request.form)
    utils.populate_provider_choices(form.provider_id, include_none=True)

    if request.method == 'POST' and form.validate():
        api.post('/collection/', dict(
            id=(id := form.id.data),
            name=form.name.data,
            provider_id=form.provider_id.data,
            doi_key=form.doi_key.data or None,
        ))
        flash(f'Collection {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('collection_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.COLLECTION_ADMIN)
def edit(id):
    collection = api.get(f'/collection/{id}')

    form = CollectionForm(request.form, data=collection)
    utils.populate_provider_choices(form.provider_id)

    if request.method == 'POST' and form.validate():
        api.put('/collection/', dict(
            id=id,
            name=form.name.data,
            provider_id=form.provider_id.data,
            doi_key=form.doi_key.data or None,
        ))
        flash(f'Collection {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('collection_edit.html', collection=collection, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@api.client(ODPScope.COLLECTION_ADMIN)
def delete(id):
    api.delete(f'/collection/{id}')
    flash(f'Collection {id} has been deleted.', category='success')
    return redirect(url_for('.index'))


@bp.route('/<id>/flag/publish', methods=('POST',))
@api.client(ODPScope.COLLECTION_FLAG_PUBLISH)
def flag_publish(id):
    api.post(f'/collection/{id}/flag', dict(
        flag_id=ODPFlag.COLLECTION_PUBLISH,
        data={},
    ))
    flash(f'{ODPFlag.COLLECTION_PUBLISH} flag has been set.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/unflag/publish', methods=('POST',))
@api.client(ODPScope.COLLECTION_FLAG_PUBLISH)
def unflag_publish(id):
    api.delete(f'/collection/{id}/flag/{ODPFlag.COLLECTION_PUBLISH}')
    flash(f'{ODPFlag.COLLECTION_PUBLISH} flag has been removed.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/doi/new')
# no @api.client because ajax
def get_new_doi(id):
    try:
        return {'doi': api.get(f'/collection/{id}/doi/new')}
    except api.ODPAPIError as e:
        return e.error_detail
