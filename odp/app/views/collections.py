from flask import Blueprint, render_template

bp = Blueprint('collections', __name__)


@bp.route('/')
def index():
    return render_template('collection_list.html')
