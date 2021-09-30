from flask import Blueprint, render_template

bp = Blueprint('roles', __name__)


@bp.route('/')
def index():
    return render_template('role_lists.html')
