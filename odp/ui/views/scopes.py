from flask import Blueprint, render_template, request, flash, redirect, url_for, abort

from odp.ui import api
from odp.ui.forms import ScopeForm

bp = Blueprint('scopes', __name__)


@bp.route('/')
def index():
    scopes = api.get('/scope/')
    return render_template('scope_list.html', scopes=scopes)


@bp.route('/<id>')
def view(id):
    scope = api.get(f'/scope/{id}')
    return render_template('scope_view.html', scope=scope)


@bp.route('/new', methods=('GET', 'POST'))
def create():
    form = ScopeForm(request.form)

    if request.method == 'POST' and form.validate():
        api.post('/scope/', dict(
            id=(id := form.id.data),
        ))
        flash(f'Scope {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('scope_edit.html', form=form)


@bp.route('/<id>/edit')
def edit(id):
    abort(404)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    api.delete(f'/scope/{id}')
    flash(f'Scope {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
