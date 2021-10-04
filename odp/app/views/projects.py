from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp.app import api
from odp.app.forms import ProjectForm

bp = Blueprint('projects', __name__)


@bp.route('/')
def index():
    projects = api.get('/project/')
    return render_template('project_list.html', projects=projects)


@bp.route('/<id>')
def view(id):
    project = api.get(f'/project/{id}')
    return render_template('project_view.html', project=project)


@bp.route('/new', methods=('GET', 'POST'))
def create():
    form = ProjectForm(request.form)

    if request.method == 'POST' and form.validate():
        api.post('/project/', dict(
            id=(id := form.id.data),
            name=form.name.data,
        ))
        flash(f'Project {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('project_create.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    project = api.get(f'/project/{id}')
    form = ProjectForm(request.form, data=project)

    if request.method == 'POST' and form.validate():
        api.put('/project/', dict(
            id=id,
            name=form.name.data,
        ))
        flash(f'Project {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('project_edit.html', project=project, form=form)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    api.delete(f'/project/{id}')
    flash(f'Project {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
