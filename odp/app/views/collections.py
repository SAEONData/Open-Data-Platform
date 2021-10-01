from flask import Blueprint, render_template

from odp.app import api

bp = Blueprint('collections', __name__)


@bp.route('/')
def index():
    collections = api.get('/collection/', sort='name')
    return render_template('collection_list.html', collections=collections)
