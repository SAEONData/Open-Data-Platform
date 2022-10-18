from flask import Blueprint, render_template, request

from odplib.const import ODPScope
from odplib.ui import api

bp = Blueprint('catalogs', __name__)


@bp.route('/')
@api.client(ODPScope.CATALOG_READ)
def index():
    page = request.args.get('page', 1)
    catalogs = api.get(f'/catalog/?page={page}')
    return render_template('catalog_list.html', catalogs=catalogs)


@bp.route('/<id>')
@api.client(ODPScope.CATALOG_READ)
def view(id):
    catalog = api.get(f'/catalog/{id}')
    return render_template('catalog_view.html', catalog=catalog)
