from flask import Blueprint, render_template

from odp.app import api

bp = Blueprint('collections', __name__)


@bp.route('/')
def index():
    collections = api.get('/collection/')
    return render_template('collection_list.html', collections=collections)


@bp.route('/<id>')
def edit(id):
    collection = api.get(f'/collection/{id}')
    return render_template('collection_edit.html', collection=collection)
