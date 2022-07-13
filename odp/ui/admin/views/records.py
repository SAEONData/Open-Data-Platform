import json

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import current_user

from odp import ODPRecordTag, ODPScope
from odp.ui import api
from odp.ui.admin.forms import RecordFilterForm, RecordForm, RecordTagEmbargoForm, RecordTagQCForm
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
    catalog_records = api.get(f'/record/{id}/catalog')
    audit_records = api.get(f'/record/{id}/audit')

    migrated_tag = next((tag for tag in record['tags'] if tag['tag_id'] == ODPRecordTag.MIGRATED), None)

    qc_tags = {
        'items': (items := [tag for tag in record['tags'] if tag['tag_id'] == ODPRecordTag.QC]),
        'total': len(items),
        'page': 1,
        'pages': 1,
    }

    embargo_tags = {
        'items': (items := [tag for tag in record['tags'] if tag['tag_id'] == ODPRecordTag.EMBARGO]),
        'total': len(items),
        'page': 1,
        'pages': 1,
    }

    return render_template(
        'record_view.html',
        record=record,
        migrated_tag=migrated_tag,
        qc_tags=qc_tags,
        embargo_tags=embargo_tags,
        catalog_records=catalog_records,
        audit_records=audit_records,
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

        try:
            record = api.post(api_route, dict(
                doi=(doi := form.doi.data) or None,
                sid=(sid := form.sid.data) or None,
                collection_id=form.collection_id.data,
                schema_id=form.schema_id.data,
                metadata=json.loads(form.metadata.data),
            ))
            flash(f'Record {doi or sid} has been created.', category='success')
            return redirect(url_for('.view', id=record['id']))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

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

        try:
            api.put(api_route + id, dict(
                doi=(doi := form.doi.data) or None,
                sid=(sid := form.sid.data) or None,
                collection_id=form.collection_id.data,
                schema_id=form.schema_id.data,
                metadata=json.loads(form.metadata.data),
            ))
            flash(f'Record {doi or sid} has been updated.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

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
@api.client(ODPScope.RECORD_QC)
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
        try:
            api.post(f'/record/{id}/tag', dict(
                tag_id=ODPRecordTag.QC,
                data={
                    'pass_': form.pass_.data,
                    'comment': form.comment.data,
                },
            ))
            flash(f'{ODPRecordTag.QC} tag has been set.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('record_tag_qc.html', record=record, form=form)


@bp.route('/<id>/untag/qc/<tag_instance_id>', methods=('POST',))
@api.client(ODPScope.RECORD_QC, ODPScope.RECORD_ADMIN, fallback_to_referrer=True)
def untag_qc(id, tag_instance_id):
    api_route = '/record/'
    if ODPScope.RECORD_ADMIN in g.user_permissions:
        api_route += 'admin/'

    api.delete(f'{api_route}{id}/tag/{tag_instance_id}')
    flash(f'{ODPRecordTag.QC} tag has been removed.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/tag/embargo', methods=('GET', 'POST'))
@api.client(ODPScope.RECORD_EMBARGO)
def tag_embargo(id):
    record = api.get(f'/record/{id}')

    if request.method == 'POST':
        form = RecordTagEmbargoForm(request.form)
    else:
        # embargo tag has cardinality 'multi', so this will always be an insert
        form = RecordTagEmbargoForm()

    if request.method == 'POST' and form.validate():
        try:
            api.post(f'/record/{id}/tag', dict(
                tag_id=ODPRecordTag.EMBARGO,
                data={
                    'start': form.start.data.isoformat(),
                    'end': form.end.data.isoformat() if form.end.data else None,
                    'comment': form.comment.data,
                },
            ))
            flash(f'{ODPRecordTag.EMBARGO} tag has been set.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('record_tag_embargo.html', record=record, form=form)


@bp.route('/<id>/untag/embargo/<tag_instance_id>', methods=('POST',))
@api.client(ODPScope.RECORD_EMBARGO, ODPScope.RECORD_ADMIN, fallback_to_referrer=True)
def untag_embargo(id, tag_instance_id):
    api_route = '/record/'
    if ODPScope.RECORD_ADMIN in g.user_permissions:
        api_route += 'admin/'

    api.delete(f'{api_route}{id}/tag/{tag_instance_id}')
    flash(f'{ODPRecordTag.EMBARGO} tag has been removed.', category='success')
    return redirect(url_for('.view', id=id))


@bp.route('/<id>/catalog/<catalog_id>')
@api.client(ODPScope.RECORD_READ)
def view_catalog_record(id, catalog_id):
    catalog_record = api.get(f'/record/{id}/catalog/{catalog_id}')
    return render_template('catalog_record_view.html', catalog_record=catalog_record)


@bp.route('/<id>/audit/<record_audit_id>')
@api.client(ODPScope.RECORD_READ)
def view_audit_detail(id, record_audit_id):
    audit_detail = api.get(f'/record/{id}/record_audit/{record_audit_id}')
    return render_template('record_audit_view.html', audit=audit_detail)


@bp.route('/<id>/tag_audit/<record_tag_audit_id>')
@api.client(ODPScope.RECORD_READ)
def view_tag_audit_detail(id, record_tag_audit_id):
    audit_detail = api.get(f'/record/{id}/record_tag_audit/{record_tag_audit_id}')
    return render_template('record_tag_audit_view.html', audit=audit_detail)
