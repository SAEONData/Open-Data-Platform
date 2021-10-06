from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp.app import api
from odp.app.forms import RoleForm

bp = Blueprint('roles', __name__)


@bp.route('/')
def index():
    roles = api.get('/role/')
    return render_template('role_list.html', roles=roles)


@bp.route('/<id>')
def view(id):
    role = api.get(f'/role/{id}')
    return render_template('role_view.html', role=role)


@bp.route('/new', methods=('GET', 'POST'))
def create():
    form = RoleForm(request.form)

    if request.method == 'POST' and form.validate():
        api.post('/role/', dict(
            id=(id := form.id.data),
            name=form.name.data,
        ))
        flash(f'Role {id} has been created.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('role_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    role = api.get(f'/role/{id}')
    form = RoleForm(request.form, data=role)

    if request.method == 'POST' and form.validate():
        api.put('/role/', dict(
            id=id,
            name=form.name.data,
        ))
        flash(f'Role {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('role_edit.html', role=role, form=form)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    api.delete(f'/role/{id}')
    flash(f'Role {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
