import json

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import current_user

from odp import ODPRecordTag, ODPScope
from odp.ui import api
from odp.ui.admin.forms import RecordFilterForm, RecordForm, RecordTagQCForm
from odp.ui.admin.views import utils

bp = Blueprint('records', __name__)


@bp.route('/')
@api.client(ODPScope.RECORD_READ)
def index():
    page = request.args.get('page', 1)
    collection_ids = request.args.getlist('collection')

    api_filter = ''
    ui_filter = ''
    for collection_id in collection_ids:
        api_filter += f'&collection_id={collection_id}'
        ui_filter += f'&collection={collection_id}'

    filter_form = RecordFilterForm(request.args)
    utils.populate_collection_choices(filter_form.collection)

    records = api.get(f'/record/?page={page}{api_filter}')
    return render_template('record_list.html', records=records, filter_=ui_filter, filter_form=filter_form)


@bp.route('/<id>')
@api.client(ODPScope.RECORD_READ)
def view(id):
    record = api.get(f'/record/{id}')
    migrated_tag = next((tag for tag in record['tags'] if tag['tag_id'] == ODPRecordTag.MIGRATED), None)
    qc_tags = {
        'items': (items := [tag for tag in record['tags'] if tag['tag_id'] == ODPRecordTag.QC]),
        'total': len(items),
        'page': 1,
        'pages': 1,
    }
    has_user_qc_tag = any(tag for tag in items if tag['user_id'] == current_user.id)
    return render_template(
        'record_view.html',
        record=record,
        migrated_tag=migrated_tag,
        qc_tags=qc_tags,
        has_user_qc_tag=has_user_qc_tag,
    )


@bp.route('/new', methods=('GET', 'POST'))
@api.client(ODPScope.RECORD_ADMIN, ODPScope.RECORD_WRITE)
def create():
    form = RecordForm(request.form)
    utils.populate_collection_choices(form.collection_id, include_none=True)
    utils.populate_schema_choices(form.schema_id, 'metadata')

    if request.method == 'POST' and form.validate():
        api_route = '/record/'
        if ODPScope.RECORD_ADMIN in g.user_permissions:
            api_route += 'admin/'

        record = api.post(api_route, dict(
            doi=(doi := form.doi.data) or None,
            sid=(sid := form.sid.data) or None,
            collection_id=form.collection_id.data,
            schema_id=form.schema_id.data,
            metadata=json.loads(form.metadata.data),
        ))
        flash(f'Record {doi or sid} has been created.', category='success')
        return redirect(url_for('.view', id=record['id']))

    return render_template('record_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.RECORD_ADMIN, ODPScope.RECORD_WRITE)
def edit(id):
    record = api.get(f'/record/{id}')

    form = RecordForm(request.form, data=record)
    utils.populate_collection_choices(form.collection_id)
    utils.populate_schema_choices(form.schema_id, 'metadata')

    if request.method == 'POST' and form.validate():
        api_route = '/record/'
        if ODPScope.RECORD_ADMIN in g.user_permissions:
            api_route += 'admin/'

        api.put(api_route + id, dict(
            doi=(doi := form.doi.data) or None,
            sid=(sid := form.sid.data) or None,
            collection_id=form.collection_id.data,
            schema_id=form.schema_id.data,
            metadata=json.loads(form.metadata.data),
        ))
        flash(f'Record {doi or sid} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('record_edit.html', record=record, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@api.client(ODPScope.RECORD_ADMIN, ODPScope.RECORD_WRITE)
def delete(id):
    api_route = '/record/'
    if ODPScope.RECORD_ADMIN in g.user_permissions:
        api_route += 'admin/'

    api.delete(api_route + id)
    flash(f'Record {id} has been deleted.', category='success')
    return redirect(url_for('.index'))


@bp.route('/<id>/tag/qc', methods=('GET', 'POST'))
@api.client(ODPScope.RECORD_TAG_QC)
def tag_qc(id):
    record = api.get(f'/record/{id}')

    # separate get/post form instantiation to resolve
    # ambiguity of missing vs false boolean field
    if request.method == 'POST':
        form = RecordTagQCForm(request.form)
    else:
        record_tag = next(
            (tag for tag in record['tags']
             if tag['tag_id'] == ODPRecordTag.QC and tag['user_id'] == current_user.id),
            None
        )
        form = RecordTagQCForm(data=record_tag['data'] if record_tag else None)

    if request.method == 'POST' and form.validate():
        api.post(f'/record/{id}/tag', dict(
            tag_id=ODPRecordTag.QC,
            data={
                'pass_': form.pass_.data,
                'comment': form.comment.data,
            },
        ))
        flash(f'{ODPRecordTag.QC} tag has been set.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('record_tag_qc.html', record=record, form=form)


@bp.route('/<id>/untag/qc', methods=('POST',))
@api.client(ODPScope.RECORD_TAG_QC)
def untag_qc(id):
    api.delete(f'/record/{id}/tag/{ODPRecordTag.QC}')
    flash(f'{ODPRecordTag.QC} tag has been removed.', category='success')
    return redirect(url_for('.view', id=id))
