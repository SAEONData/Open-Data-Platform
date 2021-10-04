from flask import Blueprint, render_template, request, flash

from odp.app import api
from odp.app.forms import ProjectForm

bp = Blueprint('projects', __name__)


@bp.route('/')
def index():
    projects = api.get('/project/')
    return render_template('project_list.html', projects=projects)


@bp.route('/<id>', methods=('GET', 'POST'))
def view(id):
    if request.method == 'GET':
        project = api.get(f'/project/{id}')
        form = ProjectForm(data=project)
    else:
        form = ProjectForm(request.form)
        if form.validate():
            project = api.put('/project/', dict(id=id, name=form.name.data))
            form = ProjectForm(data=project)
            flash('The project details have been updated.', category='success')
        else:
            flash('There are errors in the form.', category='error')

    return render_template('project_edit.html', form=form)
