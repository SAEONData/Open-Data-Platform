from flask import Blueprint, render_template, abort

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize

bp = Blueprint('tags', __name__)


@bp.route('/')
@authorize(ODPScope.TAG_READ)
@api.wrapper
def index():
    tags = api.get('/tag/')
    return render_template('tag_list.html', tags=tags)


@bp.route('/<id>')
@authorize(ODPScope.TAG_READ)
@api.wrapper
def view(id):
    tag = api.get(f'/tag/{id}')
    return render_template('tag_view.html', tag=tag)


@bp.route('/new')
def create():
    abort(404)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    abort(404)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    abort(404)
