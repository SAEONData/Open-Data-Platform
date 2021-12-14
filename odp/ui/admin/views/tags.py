from flask import Blueprint, render_template

from odp import ODPScope
from odp.ui import api

bp = Blueprint('tags', __name__)


@bp.route('/')
@api.client(ODPScope.TAG_READ)
def index():
    tags = api.get('/tag/')
    return render_template('tag_list.html', tags=tags)


@bp.route('/<id>')
@api.client(ODPScope.TAG_READ)
def view(id):
    tag = api.get(f'/tag/{id}')
    return render_template('tag_view.html', tag=tag)
