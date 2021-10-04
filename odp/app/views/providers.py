from flask import Blueprint, render_template, request, flash, redirect, url_for

from odp.app import api
from odp.app.forms import ProviderForm

bp = Blueprint('providers', __name__)


@bp.route('/')
def index():
    providers = api.get('/provider/')
    return render_template('provider_list.html', providers=providers)


@bp.route('/<id>')
def view(id):
    provider = api.get(f'/provider/{id}')
    return render_template('provider_view.html', provider=provider)


@bp.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    provider = api.get(f'/provider/{id}')
    form = ProviderForm(request.form, data=provider)

    if request.method == 'POST' and form.validate():
        api.put('/provider/', dict(
            id=id,
            name=form.name.data,
        ))
        flash(f'Provider {id} has been updated.', category='success')
        return redirect(url_for('.view', id=id))

    return render_template('provider_edit.html', provider=provider, form=form)


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    api.delete(f'/provider/{id}')
    flash(f'Provider {id} has been deleted.', category='success')
    return redirect(url_for('.index'))
