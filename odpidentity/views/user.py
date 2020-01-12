from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from hydra import HydraAdminError

from ..forms.login import LoginForm
from ..forms.signup import SignupForm
from ..lib.users import create_user_account, validate_auto_login
from ..lib.hydra import hydra_error_abort
from ..lib import exceptions as x
from . import hydra_admin

bp = Blueprint('user', __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    try:
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
                except x.ODPIdentityError as e:
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
            except x.ODPIdentityError as e:
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


@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    try:
        user = None
        error = None
        form = None

        try:
            if request.method == 'GET':
                challenge = request.args.get('challenge')
                login_request = hydra_admin.get_login_request(challenge)
                authenticated = login_request['skip']
                if authenticated:
                    raise x.ODPSignupLoggedInUser
                form = SignupForm(challenge=challenge)

            else:
                # it's a post from the user
                form = SignupForm()
                challenge = form.challenge.data
                if form.validate():  # calls validate_user_signup
                    user = create_user_account(form.email.data, form.password.data)

        except x.ODPIdentityError as e:
            error = e

        if user:
            redirect_to = hydra_admin.accept_login_request(challenge, user.id)
        elif error:
            redirect_to = hydra_admin.reject_login_request(challenge, error.error_code, error.error_description)
        else:
            return render_template('signup.html', form=form)

        return redirect(redirect_to)

    except HydraAdminError as e:
        # TODO we have to rollback the user creation, or keep it in an inactive state, if we arrive here
        hydra_error_abort(e)


@bp.route('/profile')
@login_required
def profile():
    return 'User profile page'
