from flask import Blueprint, render_template

from odp.app import api

bp = Blueprint('projects', __name__)


@bp.route('/')
def index():
    projects = api.get('/project/')
    return render_template('project_list.html', projects=projects)


@bp.route('/<id>')
def edit(id):
    project = api.get(f'/project/{id}')
    return render_template('project_edit.html', project=project)
