from flask import Blueprint, render_template, request

from odp import ODPScope
from odp.ui import api

bp = Blueprint('vocabularies', __name__)


@bp.route('/')
@api.client(ODPScope.VOCABULARY_READ)
def index():
    page = request.args.get('page', 1)
    vocabularies = api.get(f'/vocabulary/?page={page}')
    return render_template('vocabulary_list.html', vocabularies=vocabularies)


@bp.route('/<id>')
@api.client(ODPScope.VOCABULARY_READ)
def view(id):
    vocabulary = api.get(f'/vocabulary/{id}')
    return render_template('vocabulary_view.html', vocabulary=vocabulary)
