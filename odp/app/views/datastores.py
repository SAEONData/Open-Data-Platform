from flask import Blueprint, render_template

bp = Blueprint('datastores', __name__)


@bp.route('/')
def index():
    return render_template('datastore_lists.html')
