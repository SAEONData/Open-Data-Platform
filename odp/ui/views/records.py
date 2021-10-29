from flask import Blueprint, render_template

bp = Blueprint('records', __name__)


@bp.route('/')
def index():
    return render_template('record_lists.html')
