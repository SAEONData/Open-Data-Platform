from flask import Blueprint, render_template, request

from odp import ODPScope
from odp.ui import api

bp = Blueprint('catalogues', __name__)


@bp.route('/')
@api.client(ODPScope.CATALOGUE_READ)
def index():
    page = request.args.get('page', 1)
    catalogues = api.get(f'/catalogue/?page={page}')
    return render_template('catalogue_list.html', catalogues=catalogues)


@bp.route('/<id>')
@api.client(ODPScope.CATALOGUE_READ)
def view(id):
    catalogue = api.get(f'/catalogue/{id}')
    return render_template('catalogue_view.html', catalogue=catalogue)
