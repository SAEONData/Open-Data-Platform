import json

from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize
from odp.ui.forms import RecordForm

bp = Blueprint('records', __name__)


@bp.route('/')
@authorize(ODPScope.RECORD_READ)
@api.wrapper
def index():
    records = api.get('/record/')
    return render_template('record_list.html', records=records)


@bp.route('/<id>')
@authorize(ODPScope.RECORD_READ)
@api.wrapper
def view(id):
    record = api.get(f'/record/{id}')
    return render_template('record_view.html', record=record)


@bp.route('/new', methods=('GET', 'POST'))
@authorize(ODPScope.RECORD_CREATE)
@api.wrapper
def create():
    collections = api.get('/collection/', sort='name')
    schemas = api.get('/schema/')

    form = RecordForm(request.form)
    form.collection_id.choices = [
        (collection['id'], collection['name'])
        for collection in collections
    ]
    form.schema_id.choices = [
        (schema['id'], schema['id'])
        for schema in schemas
    ]

    if request.method == 'POST' and form.validate():
        record = api.post('/record/', dict(
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
@authorize(ODPScope.RECORD_MANAGE)
@api.wrapper
def edit(id):
    record = api.get(f'/record/{id}')
    collections = api.get('/collection/', sort='name')
    schemas = api.get('/schema/')

    form = RecordForm(request.form, data=record)
    form.collection_id.choices = [
        (collection['id'], collection['name'])
        for collection in collections
    ]
    form.schema_id.choices = [
        (schema['id'], schema['id'])
        for schema in schemas
    ]

    if request.method == 'POST' and form.validate():
        api.put(f'/record/{id}', dict(
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
@authorize(ODPScope.RECORD_MANAGE)
@api.wrapper
def delete(id):
    api.delete(f'/record/{id}')
    flash(f'Record {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
