from flask import Blueprint, render_template

from odp.app import api

bp = Blueprint('projects', __name__)


@bp.route('/')
def index():
    projects = api.get('/project/', sort='name')
    return render_template('project_list.html', projects=projects)
