from flask import Blueprint, render_template, request

from odp import ODPScope
from odp.ui.public.forms import SearchForm
from odp_uilib import api

bp = Blueprint('catalog', __name__)


@bp.route('/')
@api.client(ODPScope.CATALOG_READ)
def index():
    page = request.args.get('page', 1)
    text_q = request.args.get('q')

    api_filter = ''
    ui_filter = ''
    if text_q:
        api_filter += f'&text_q={text_q}'
        ui_filter += f'&q={text_q}'

    records = api.get(f'/catalog/SAEON/records?page={page}{api_filter}')
    return render_template(
        'record_list.html',
        records=records,
        filter_=ui_filter,
        search_form=SearchForm(request.args),
    )


@bp.route('/<path:id>')
@api.client(ODPScope.CATALOG_READ)
def view(id):
    record = api.get(f'/catalog/SAEON/records/{id}')
    return render_template(
        'record_view.html',
        record=record,
    )
