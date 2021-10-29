from flask import Blueprint, render_template

bp = Blueprint('tags', __name__)


@bp.route('/')
def index():
    return render_template('tag_lists.html')
