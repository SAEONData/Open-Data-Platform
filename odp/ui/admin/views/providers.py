from flask import Blueprint, flash, redirect, render_template, request, url_for

from odp.ui.admin.forms import ProviderForm
from odplib.const import ODPScope
from odplib.ui import api

bp = Blueprint('providers', __name__)


@bp.route('/')
@api.client(ODPScope.PROVIDER_READ)
def index():
    page = request.args.get('page', 1)
    providers = api.get(f'/provider/?page={page}')
    return render_template('provider_list.html', providers=providers)


@bp.route('/<id>')
@api.client(ODPScope.PROVIDER_READ)
def view(id):
    provider = api.get(f'/provider/{id}')
    return render_template('provider_view.html', provider=provider)


@bp.route('/new', methods=('GET', 'POST'))
@api.client(ODPScope.PROVIDER_ADMIN)
def create():
    form = ProviderForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            api.post('/provider/', dict(
                id=(id := form.id.data),
                name=form.name.data,
            ))
            flash(f'Provider {id} has been created.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('provider_edit.html', form=form)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
@api.client(ODPScope.PROVIDER_ADMIN)
def edit(id):
    provider = api.get(f'/provider/{id}')
    form = ProviderForm(request.form, data=provider)

    if request.method == 'POST' and form.validate():
        try:
            api.put('/provider/', dict(
                id=id,
                name=form.name.data,
            ))
            flash(f'Provider {id} has been updated.', category='success')
            return redirect(url_for('.view', id=id))

        except api.ODPAPIError as e:
            if response := api.handle_error(e):
                return response

    return render_template('provider_edit.html', provider=provider, form=form)


@bp.route('/<id>/delete', methods=('POST',))
@api.client(ODPScope.PROVIDER_ADMIN)
def delete(id):
    api.delete(f'/provider/{id}')
    flash(f'Provider {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
