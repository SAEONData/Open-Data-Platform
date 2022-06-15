from flask import Blueprint, flash, redirect, render_template, request, url_for

from odp import ODPCollectionTag, ODPScope
from odp.ui import api
from odp.ui.admin.forms import CollectionForm
from odp.ui.admin.views import utils

bp = Blueprint('collections', __name__)


@bp.route('/')
@api.client(ODPScope.COLLECTION_READ)
def index():
    page = request.args.get('page', 1)
    collections = api.get(f'/collection/?page={page}')
    return render_template('collection_list.html', collections=collections)


@bp.route('/<id>')
@api.client(ODPScope.COLLECTION_READ)
def view(id):
    collection = api.get(f'/collection/{id}')
    publish_tag = next(
        (tag for tag in collection['tags']
         if tag['tag_id'] == ODPCollectionTag.PUBLISH),
        None
    )
    archive_tag = next(
        (tag for tag in collection['tags']
         if tag['tag_id'] == ODPCollectionTag.ARCHIVE),
        None
    )
    return render_template(
        'collection_view.html', collection=collection,
        publish_tag=publish_tag, archive_tag=archive_tag,
    )


@bp.route('/new', methods=('GET', 'POST'))
@api.client(ODPScope.COLLECTION_ADMIN)
def create():
    form = CollectionForm(request.form)
    utils.populate_provider_choices(form.provider_id, include_none=True)

    if request.method == 'POST' and form.validate():
        try:
            api.post('/collection/', dict(
                id=(id := form.id.data),
                name=form.name.data,
                provider_id=form.provider_id.data,
                doi_key=form.doi_key.data or None,
            ))
            flash(f'Collection {id} has been created.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('collection_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.COLLECTION_ADMIN)
def edit(id):
    collection = api.get(f'/collection/{id}')

    form = CollectionForm(request.form, data=collection)
    utils.populate_provider_choices(form.provider_id)

    if request.method == 'POST' and form.validate():
        try:
            api.put('/collection/', dict(
                id=id,
                name=form.name.data,
                provider_id=form.provider_id.data,
                doi_key=form.doi_key.data or None,
            ))
            flash(f'Collection {id} has been updated.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('collection_edit.html', collection=collection, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@api.client(ODPScope.COLLECTION_ADMIN)
def delete(id):
    api.delete(f'/collection/{id}')
    flash(f'Collection {id} has been deleted.', category='success')
    return redirect(url_for('.index'))


@bp.route('/<id>/tag/publish', methods=('POST',))
@api.client(ODPScope.COLLECTION_PUBLISH, fallback_to_referrer=True)
def tag_publish(id):
    api.post(f'/collection/{id}/tag', dict(
        tag_id=ODPCollectionTag.PUBLISH,
        data={},
    ))
    flash(f'{ODPCollectionTag.PUBLISH} tag has been set.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/untag/publish', methods=('POST',))
@api.client(ODPScope.COLLECTION_PUBLISH, fallback_to_referrer=True)
def untag_publish(id):
    api.delete(f'/collection/{id}/tag/{ODPCollectionTag.PUBLISH}')
    flash(f'{ODPCollectionTag.PUBLISH} tag has been removed.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/tag/archive', methods=('POST',))
@api.client(ODPScope.COLLECTION_ARCHIVE, fallback_to_referrer=True)
def tag_archive(id):
    api.post(f'/collection/{id}/tag', dict(
        tag_id=ODPCollectionTag.ARCHIVE,
        data={},
    ))
    flash(f'{ODPCollectionTag.ARCHIVE} tag has been set.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/untag/archive', methods=('POST',))
@api.client(ODPScope.COLLECTION_ARCHIVE, fallback_to_referrer=True)
def untag_archive(id):
    api.delete(f'/collection/{id}/tag/{ODPCollectionTag.ARCHIVE}')
    flash(f'{ODPCollectionTag.ARCHIVE} tag has been removed.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/doi/new')
# no @api.client because ajax
def get_new_doi(id):
    try:
        return {'doi': api.get(f'/collection/{id}/doi/new')}
    except api.ODPAPIError as e:
        return e.error_detail
