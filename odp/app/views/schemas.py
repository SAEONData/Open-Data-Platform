from flask import Blueprint, render_template

bp = Blueprint('schemas', __name__)


@bp.route('/')
def index():
    return render_template('schema_lists.html')
