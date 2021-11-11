from flask import Blueprint, render_template, abort

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize

bp = Blueprint('catalogues', __name__)


@bp.route('/')
@authorize(ODPScope.CATALOGUE_READ)
@api.wrapper
def index():
    catalogues = api.get('/catalogue/')
    return render_template('catalogue_list.html', catalogues=catalogues)


@bp.route('/<id>')
@authorize(ODPScope.CATALOGUE_READ)
@api.wrapper
def view(id):
    catalogue = api.get(f'/catalogue/{id}')
    return render_template('catalogue_view.html', catalogue=catalogue)


@bp.route('/new')
def create():
    abort(404)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    abort(404)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    abort(404)
