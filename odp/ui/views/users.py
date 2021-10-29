from flask import Blueprint, render_template, request, flash, redirect, url_for, abort

from odp.ui import api
from odp.ui.forms import UserForm

bp = Blueprint('users', __name__)


@bp.route('/')
def index():
    users = api.get('/user/')
    return render_template('user_list.html', users=users)


@bp.route('/<id>')
def view(id):
    user = api.get(f'/user/{id}')
    return render_template('user_view.html', user=user)


@bp.route('/new')
def create():
    abort(404)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    user = api.get(f'/user/{id}')
    form = UserForm(request.form, data=user)

    if request.method == 'POST' and form.validate():
        api.put('/user/', dict(
            id=id,
            active=form.active.data,
        ))
        flash(f'User {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('user_edit.html', user=user, form=form)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    api.delete(f'/user/{id}')
    flash(f'User {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
