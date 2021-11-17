from flask import Blueprint, render_template, request, flash, redirect, url_for, abort

from odp import ODPScope
from odp.ui import api
from odp.ui.auth import authorize
from odp.ui.forms import UserForm
from odp.ui.views import utils

bp = Blueprint('users', __name__)


@bp.route('/')
@authorize(ODPScope.USER_READ)
@api.wrapper
def index():
    users = api.get('/user/')
    return render_template('user_list.html', users=users)


@bp.route('/<id>')
@authorize(ODPScope.USER_READ)
@api.wrapper
def view(id):
    user = api.get(f'/user/{id}')
    return render_template('user_view.html', user=user)


@bp.route('/new')
@authorize(ODPScope.USER_ADMIN)
def create():
    abort(404)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@authorize(ODPScope.USER_ADMIN)
@api.wrapper
def edit(id):
    user = api.get(f'/user/{id}')

    # separate get/post form instantiation to resolve
    # ambiguity of missing vs empty multiselect field
    if request.method == 'POST':
        form = UserForm(request.form)
    else:
        form = UserForm(data=user)

    utils.populate_role_choices(form.role_ids)

    if request.method == 'POST' and form.validate():
        api.put('/user/', dict(
            id=id,
            active=form.active.data,
            role_ids=form.role_ids.data,
        ))
        flash(f'User {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('user_edit.html', user=user, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@authorize(ODPScope.USER_ADMIN)
@api.wrapper
def delete(id):
    api.delete(f'/user/{id}')
    flash(f'User {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
