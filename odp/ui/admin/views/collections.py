from flask import Blueprint, flash, redirect, render_template, request, url_for

from odp import ODPCollectionTag, ODPScope
from odp.ui import api
from odp.ui.admin.forms import CollectionForm
from odp.ui.admin.views import utils

bp = Blueprint('collections', __name__)


def get_tag_instance(collection, tag_id):
    return next(
        (tag for tag in collection['tags'] if tag['tag_id'] == tag_id),
        None
    )


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
    audit_records = api.get(f'/collection/{id}/audit')
    return render_template(
        'collection_view.html',
        collection=collection,
        ready_tag=get_tag_instance(collection, ODPCollectionTag.READY),
        frozen_tag=get_tag_instance(collection, ODPCollectionTag.FROZEN),
        audit_records=audit_records,
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


@bp.route('/<id>/tag/ready', methods=('POST',))
@api.client(ODPScope.COLLECTION_ADMIN, fallback_to_referrer=True)
def tag_ready(id):
    api.post(f'/collection/{id}/tag', dict(
        tag_id=ODPCollectionTag.READY,
        data={},
    ))
    flash(f'{ODPCollectionTag.READY} tag has been set.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/untag/ready', methods=('POST',))
@api.client(ODPScope.COLLECTION_ADMIN, fallback_to_referrer=True)
def untag_ready(id):
    collection = api.get(f'/collection/{id}')
    if ready_tag := get_tag_instance(collection, ODPCollectionTag.READY):
        api.delete(f'/collection/admin/{id}/tag/{ready_tag["id"]}')
        flash(f'{ODPCollectionTag.READY} tag has been removed.', category='success')

    return redirect(url_for('.view', id=id))


@bp.route('/<id>/tag/frozen', methods=('POST',))
@api.client(ODPScope.COLLECTION_ADMIN, fallback_to_referrer=True)
def tag_frozen(id):
    api.post(f'/collection/{id}/tag', dict(
        tag_id=ODPCollectionTag.FROZEN,
        data={},
    ))
    flash(f'{ODPCollectionTag.FROZEN} tag has been set.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/untag/frozen', methods=('POST',))
@api.client(ODPScope.COLLECTION_ADMIN, fallback_to_referrer=True)
def untag_frozen(id):
    collection = api.get(f'/collection/{id}')
    if frozen_tag := get_tag_instance(collection, ODPCollectionTag.FROZEN):
        api.delete(f'/collection/admin/{id}/tag/{frozen_tag["id"]}')
        flash(f'{ODPCollectionTag.FROZEN} tag has been removed.', category='success')

    return redirect(url_for('.view', id=id))


@bp.route('/<id>/doi/new')
# no @api.client because ajax
def get_new_doi(id):
    try:
        return {'doi': api.get(f'/collection/{id}/doi/new')}
    except api.ODPAPIError as e:
        return e.error_detail


@bp.route('/<id>/audit/<collection_audit_id>')
@api.client(ODPScope.COLLECTION_READ)
def view_audit_detail(id, collection_audit_id):
    audit_detail = api.get(f'/collection/{id}/collection_audit/{collection_audit_id}')
    return render_template('collection_audit_view.html', audit=audit_detail)


@bp.route('/<id>/tag_audit/<collection_tag_audit_id>')
@api.client(ODPScope.COLLECTION_READ)
def view_tag_audit_detail(id, collection_tag_audit_id):
    audit_detail = api.get(f'/collection/{id}/collection_tag_audit/{collection_tag_audit_id}')
    return render_template('collection_tag_audit_view.html', audit=audit_detail)
