from flask import Blueprint, render_template, request

from odp import ODPScope
from odp.ui import api
from odp.ui.public.forms import SearchForm

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

    search_form = SearchForm(request.args)

    records = api.get(f'/catalog/SAEON/records?page={page}{api_filter}')
    return render_template(
        'record_list.html',
        records=records,
        filter_=ui_filter,
        search_form=search_form,
    )
