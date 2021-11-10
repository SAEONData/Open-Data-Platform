from flask import Blueprint, render_template, abort

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize

bp = Blueprint('schemas', __name__)


@bp.route('/')
@authorize(ODPScope.SCHEMA_READ)
@api.wrapper
def index():
    schemas = api.get('/schema/')
    return render_template('schema_list.html', schemas=schemas)


@bp.route('/<id>')
@authorize(ODPScope.SCHEMA_READ)
@api.wrapper
def view(id):
    schema = api.get(f'/schema/{id}')
    return render_template('schema_view.html', schema=schema)


@bp.route('/new')
def create():
    abort(404)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    abort(404)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    abort(404)
