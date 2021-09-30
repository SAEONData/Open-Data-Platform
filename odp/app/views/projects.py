from flask import Blueprint, render_template

bp = Blueprint('projects', __name__)


@bp.route('/')
def index():
    return render_template('project_list.html')
