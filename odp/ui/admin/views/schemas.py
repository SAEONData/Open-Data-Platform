from flask import Blueprint, render_template, request

from odp import ODPScope
from odp.ui import api

bp = Blueprint('schemas', __name__)


@bp.route('/')
@api.client(ODPScope.SCHEMA_READ)
def index():
    page = request.args.get('page', 1)
    schemas = api.get(f'/schema/?schema_type=metadata&page={page}')
    return render_template('schema_list.html', schemas=schemas)


@bp.route('/<id>')
@api.client(ODPScope.SCHEMA_READ)
def view(id):
    schema = api.get(f'/schema/{id}')
    return render_template('schema_view.html', schema=schema)
