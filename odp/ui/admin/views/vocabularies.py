from flask import Blueprint, flash, redirect, render_template, request, url_for

from odp import ODPScope, ODPVocabulary
from odp.ui import api
from odp.ui.admin.forms import VocabularyTermInfrastructureForm, VocabularyTermProjectForm
from odp.ui.admin.views import utils

bp = Blueprint('vocabularies', __name__)


@bp.route('/')
@api.client(ODPScope.VOCABULARY_READ)
def index():
    page = request.args.get('page', 1)
    vocabularies = api.get(f'/vocabulary/?page={page}')
    return render_template('vocabulary_list.html', vocabularies=vocabularies)


@bp.route('/<id>')
@api.client(ODPScope.VOCABULARY_READ)
def view(id):
    vocabulary = api.get(f'/vocabulary/{id}')
    audit_records = api.get(f'/vocabulary/{id}/audit')

    return render_template(
        'vocabulary_view.html',
        vocabulary=vocabulary,
        terms=utils.pagify(vocabulary['terms']),
        audit_records=audit_records,
    )


@bp.route('/<id>/audit/<audit_id>')
@api.client(ODPScope.VOCABULARY_READ)
def view_audit_detail(id, audit_id):
    audit_detail = api.get(f'/vocabulary/{id}/audit/{audit_id}')
    return render_template('vocabulary_audit_view.html', audit=audit_detail)


@bp.route(f'/{ODPVocabulary.INFRASTRUCTURE}/new', methods=('GET', 'POST'))
@api.client(ODPScope.VOCABULARY_INFRASTRUCTURE)
def create_infrastructure_term():
    return _create_term(ODPVocabulary.INFRASTRUCTURE.value, VocabularyTermInfrastructureForm, 'name', 'description')


@bp.route(f'/{ODPVocabulary.INFRASTRUCTURE}/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.VOCABULARY_INFRASTRUCTURE)
def edit_infrastructure_term(id):
    return _edit_term(ODPVocabulary.INFRASTRUCTURE.value, id, VocabularyTermInfrastructureForm, 'name', 'description')


@bp.route(f'/{ODPVocabulary.INFRASTRUCTURE}/<id>/delete', methods=('POST',))
@api.client(ODPScope.VOCABULARY_INFRASTRUCTURE, fallback_to_referrer=True)
def delete_infrastructure_term(id):
    return _delete_term(ODPVocabulary.INFRASTRUCTURE.value, id)


@bp.route(f'/{ODPVocabulary.PROJECT}/new', methods=('GET', 'POST'))
@api.client(ODPScope.VOCABULARY_PROJECT)
def create_project_term():
    return _create_term(ODPVocabulary.PROJECT.value, VocabularyTermProjectForm, 'title', 'description')


@bp.route(f'/{ODPVocabulary.PROJECT}/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.VOCABULARY_PROJECT)
def edit_project_term(id):
    return _edit_term(ODPVocabulary.PROJECT.value, id, VocabularyTermProjectForm, 'title', 'description')


@bp.route(f'/{ODPVocabulary.PROJECT}/<id>/delete', methods=('POST',))
@api.client(ODPScope.VOCABULARY_PROJECT, fallback_to_referrer=True)
def delete_project_term(id):
    return _delete_term(ODPVocabulary.PROJECT.value, id)


def _create_term(vocab_id, form_cls, *data_fields):
    vocabulary = api.get(f'/vocabulary/{vocab_id}')
    form = form_cls(request.form)

    if request.method == 'POST' and form.validate():
        try:
            api.post(f'/vocabulary/{vocab_id}/term', dict(
                id=(id := form.id.data),
                data={
                    field: form[field].data
                    for field in data_fields
                },
            ))
            flash(f'{vocab_id} {id} has been created.', category='success')
            return redirect(url_for('.view', id=vocab_id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template(
        f'vocabulary_term_{vocab_id.lower()}.html',
        vocabulary=vocabulary,
        form=form,
    )


def _edit_term(vocab_id, term_id, form_cls, *data_fields):
    vocabulary = api.get(f'/vocabulary/{vocab_id}')
    term = next((t for t in vocabulary['terms'] if t['id'] == term_id), None)
    form = form_cls(request.form, data=term['data'])

    if request.method == 'POST' and form.validate():
        try:
            api.put(f'/vocabulary/{vocab_id}/term', dict(
                id=form.id.data,
                data={
                    field: form[field].data
                    for field in data_fields
                },
            ))
            flash(f'{vocab_id} {term_id} has been updated.', category='success')
            return redirect(url_for('.view', id=vocab_id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template(
        f'vocabulary_term_{vocab_id.lower()}.html',
        vocabulary=vocabulary,
        term=term,
        form=form,
    )


def _delete_term(vocab_id, term_id):
    api.delete(f'/vocabulary/{vocab_id}/term/{term_id}')
    flash(f'{vocab_id} {term_id} has been deleted.', category='success')
    return redirect(url_for('.view', id=vocab_id))
