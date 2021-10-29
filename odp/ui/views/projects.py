from flask import Blueprint, render_template, request, flash, redirect, url_for
from markupsafe import Markup

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize
from odp.ui.forms import ProjectForm

bp = Blueprint('projects', __name__)


@bp.route('/')
@authorize(ODPScope.PROJECT_READ)
def index():
    projects = api.get('/project/')
    return render_template('project_list.html', projects=projects)


@bp.route('/<id>')
@authorize(ODPScope.PROJECT_READ)
def view(id):
    project = api.get(f'/project/{id}')
    return render_template('project_view.html', project=project)


@bp.route('/new', methods=('GET', 'POST'))
@authorize(ODPScope.PROJECT_ADMIN)
def create():
    collections = api.get('/collection/')

    form = ProjectForm(request.form)
    form.collection_ids.choices = [
        (collection['id'], Markup(f"{collection['id']} &mdash; {collection['name']}"))
        for collection in collections
    ]

    if request.method == 'POST' and form.validate():
        api.post('/project/', dict(
            id=(id := form.id.data),
            name=form.name.data,
            collection_ids=form.collection_ids.data,
        ))
        flash(f'Project {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('project_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@authorize(ODPScope.PROJECT_ADMIN)
def edit(id):
    project = api.get(f'/project/{id}')
    collections = api.get('/collection/')

    # separate get/post form instantiation to resolve
    # ambiguity of missing vs empty multiselect field
    if request.method == 'POST':
        form = ProjectForm(request.form)
    else:
        form = ProjectForm(data=project)

    form.collection_ids.choices = [
        (collection['id'], Markup(f"{collection['id']} &mdash; {collection['name']}"))
        for collection in collections
    ]

    if request.method == 'POST' and form.validate():
        api.put('/project/', dict(
            id=id,
            name=form.name.data,
            collection_ids=form.collection_ids.data,
        ))
        flash(f'Project {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('project_edit.html', project=project, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@authorize(ODPScope.PROJECT_ADMIN)
def delete(id):
    api.delete(f'/project/{id}')
    flash(f'Project {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
