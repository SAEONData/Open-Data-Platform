from flask import Blueprint, render_template, redirect, url_for, request

from ..forms.registration import RegistrationForm
from ..lib.users import create_user_account

bp = Blueprint('user', __name__)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        create_user_account(form.email.data, form.password.data)
        # todo confirmation email
        return redirect(url_for('hydra.login'))

    return render_template('register.html', form=form)
