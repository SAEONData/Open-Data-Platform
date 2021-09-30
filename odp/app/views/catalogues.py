from flask import Blueprint, render_template

bp = Blueprint('catalogues', __name__)


@bp.route('/')
def index():
    return render_template('catalogue_lists.html')
