from flask import Blueprint, render_template, redirect, url_for, request
from flask_wtf import FlaskForm

from hydra import HydraAdminError

from . import hydra_error_page, encode_token, decode_token
from .. import hydra_admin
from ..forms.signup import SignupForm
from ..lib import exceptions as x
from ..lib.users import create_user_account, validate_user_signup
from .account import send_verification_email

bp = Blueprint('signup', __name__)


@bp.route('/', methods=('GET', 'POST'))
def signup():
    """
    User signup view. The token ensures that we can only access this view in the context of the Hydra login workflow.
    """
    token = request.args.get('token')
    try:
        login_request, challenge, params = decode_token(token, 'login')

        form = SignupForm()
        try:
            if request.method == 'GET':
                # if the user is already authenticated with Hydra, their user id is associated with the login challenge;
                # we cannot then associate a new user id with the same login challenge
                authenticated = login_request['skip']
                if authenticated:
                    raise x.ODPSignupAuthenticatedUser

            else:  # POST
                if form.validate():
                    email = form.email.data
                    password = form.password.data
                    try:
                        validate_user_signup(email, password)
                        user = create_user_account(email, password)

                        # the signup (and login) is completed via email verification
                        send_verification_email(email, challenge)
                        verify_token = encode_token(challenge, 'signup.verify', email=email)
                        return redirect(url_for('.verify', token=verify_token))

                    except x.ODPEmailInUse:
                        form.email.errors.append("The email address is already associated with a user account.")

                    except x.ODPPasswordComplexityError:
                        form.password.errors.append("The password does not meet the minimum complexity requirements.")

            return render_template('signup.html', form=form, token=token)

        except x.ODPIdentityError as e:
            # any other validation error (e.g. user already authenticated) => reject login
            redirect_to = hydra_admin.reject_login_request(challenge, e.error_code, e.error_description)
            return redirect(redirect_to)

    except HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/verify', methods=('GET', 'POST'))
def verify():
    """
    View for sending a verification email. The token ensures that we can only get here from the user signup view.
    """
    token = request.args.get('token')
    try:
        login_request, challenge, params = decode_token(token, 'signup.verify')

        form = FlaskForm()
        email = params.get('email')

        if request.method == 'POST':
            send_verification_email(email, challenge)

        return render_template('signup_verify.html', form=form, token=token)

    except HydraAdminError as e:
        return hydra_error_page(e)
