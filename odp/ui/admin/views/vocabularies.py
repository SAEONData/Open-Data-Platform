from flask import Blueprint, flash, redirect, render_template, request, url_for

from odp import ODPScope, ODPVocabulary
from odp.ui import api
from odp.ui.admin.forms import VocabularyTermProjectForm

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
    terms = {
        'items': (items := vocabulary['terms']),
        'total': len(items),
        'page': 1,
        'pages': 1,
    }
    return render_template('vocabulary_view.html', vocabulary=vocabulary, terms=terms)


@bp.route(f'/{ODPVocabulary.PROJECT}/new', methods=('GET', 'POST'))
@api.client(ODPScope.VOCABULARY_PROJECT)
def create_project_term():
    vocabulary = api.get(f'/vocabulary/{ODPVocabulary.PROJECT}')
    form = VocabularyTermProjectForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            api.post(f'/vocabulary/{ODPVocabulary.PROJECT}/', dict(
                id=(id := form.id.data),
                data={
                    'title': form.title.data,
                    'description': form.description.data,
                },
            ))
            flash(f'{ODPVocabulary.PROJECT} {id} has been created.', category='success')
            return redirect(url_for('.view', id=ODPVocabulary.PROJECT.value))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('vocabulary_term_project.html', vocabulary=vocabulary, form=form)


@bp.route(f'/{ODPVocabulary.PROJECT}/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.VOCABULARY_PROJECT)
def edit_project_term(id):
    vocabulary = api.get(f'/vocabulary/{ODPVocabulary.PROJECT}')
    term = next((t for t in vocabulary['terms'] if t['id'] == id), None)
    form = VocabularyTermProjectForm(request.form, data=term['data'])

    if request.method == 'POST' and form.validate():
        try:
            api.put(f'/vocabulary/{ODPVocabulary.PROJECT}/', dict(
                id=form.id.data,
                data={
                    'title': form.title.data,
                    'description': form.description.data,
                },
            ))
            flash(f'{ODPVocabulary.PROJECT} {id} has been updated.', category='success')
            return redirect(url_for('.view', id=ODPVocabulary.PROJECT.value))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('vocabulary_term_project.html', vocabulary=vocabulary, term=term, form=form)


@bp.route(f'/{ODPVocabulary.PROJECT}/<id>/delete', methods=('POST',))
@api.client(ODPScope.VOCABULARY_PROJECT, fallback_to_referrer=True)
def delete_project_term(id):
    api.delete(f'/vocabulary/{ODPVocabulary.PROJECT}/{id}')
    flash(f'{ODPVocabulary.PROJECT} {id} has been deleted.', category='success')
    return redirect(url_for('.view', id=ODPVocabulary.PROJECT.value))
