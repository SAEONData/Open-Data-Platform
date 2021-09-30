from flask import Blueprint, render_template

bp = Blueprint('providers', __name__)


@bp.route('/')
def index():
    return render_template('provider_lists.html')
