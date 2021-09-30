from flask import Blueprint, render_template

bp = Blueprint('scopes', __name__)


@bp.route('/')
def index():
    return render_template('scope_lists.html')
