from flask import Blueprint, render_template

bp = Blueprint('users', __name__)


@bp.route('/')
def index():
    return render_template('user_lists.html')
