from flask import Blueprint, render_template, request

from odp import ODPScope
from odp_uilib import api

bp = Blueprint('tags', __name__)


@bp.route('/')
@api.client(ODPScope.TAG_READ)
def index():
    page = request.args.get('page', 1)
    tags = api.get(f'/tag/?page={page}')
    return render_template('tag_list.html', tags=tags)


@bp.route('/<id>')
@api.client(ODPScope.TAG_READ)
def view(id):
    tag = api.get(f'/tag/{id}')
    return render_template('tag_view.html', tag=tag)
