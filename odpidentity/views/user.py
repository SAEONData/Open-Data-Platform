from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from hydra import HydraAdminError

from ..forms.login import LoginForm
from ..forms.registration import RegistrationForm
from ..lib.users import create_user_account, validate_auto_login
from ..lib.hydra import create_hydra_admin, hydra_error_abort
from ..lib import exceptions as x

bp = Blueprint('user', __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    try:
        hydra_admin = create_hydra_admin()
        user_id = None
        error = None
        form = None

        if request.method == 'GET':
            challenge = request.args.get('challenge')
            login_request = hydra_admin.get_login_request(challenge)
            authenticated = login_request['skip']

            # if already authenticated, we'll wind up with either a user_id or an error
            if authenticated:
                user_id = login_request['subject']
                try:
                    validate_auto_login(user_id)
                except x.ODPLoginError as e:
                    user_id = None
                    error = e

            # otherwise, we prepare a login form
            else:
                form = LoginForm(login_challenge=challenge)

        else:
            # it's a post from the user
            form = LoginForm()
            challenge = form.login_challenge.data
            try:
                if form.validate():  # calls validate_user_login
                    user_id = form.user_id
            except x.ODPLoginError as e:
                error = e

        if user_id:
            redirect_to = hydra_admin.accept_login_request(challenge, user_id)
        elif error:
            redirect_to = hydra_admin.reject_login_request(challenge, error.error_code, error.error_description)
        else:
            return render_template('login.html', form=form)

        return redirect(redirect_to)

    except HydraAdminError as e:
        hydra_error_abort(e)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        create_user_account(form.email.data, form.password.data)
        # todo confirmation email
        return redirect(url_for('oauth2.login'))

    return render_template('register.html', form=form)


@bp.route('/profile')
@login_required
def profile():
    return 'User profile page'
