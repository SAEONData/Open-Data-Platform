from flask import Blueprint, render_template, redirect, url_for, request

from hydra import HydraAdminError

from .. import hydra_admin
from ..forms.credentials import CredentialsForm
from ..forms.verify_email import VerifyEmailForm
from ..lib import exceptions as x
from ..lib.hydra import hydra_error_page
from ..lib.users import validate_auto_login, validate_user_login
from .account import send_verification_email

bp = Blueprint('login', __name__)


@bp.route('/', methods=('GET', 'POST'))
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
                form = CredentialsForm(challenge=challenge)

        else:
            # it's a post from the user
            form = CredentialsForm()
            challenge = form.challenge.data
            try:
                if form.validate():
                    email = form.email.data
                    password = form.password.data
                    try:
                        user = validate_user_login(email, password)
                        user_id = user.id

                    except x.ODPUserNotFound:
                        form.email.errors.append("The email address is not associated with any user account.")

                    except x.ODPIncorrectPassword:
                        form.email.errors.append("The email address and password do not match.")

                    except x.ODPEmailNotVerified:
                        send_verification_email(email, challenge)
                        return redirect(url_for('.verify', email=email, challenge=challenge))

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
        return hydra_error_page(e)


@bp.route('/verify', methods=('GET', 'POST'))
def verify():
    if request.method == 'GET':
        challenge = request.args.get('challenge')
        email = request.args.get('email')
        form = VerifyEmailForm(challenge=challenge, email=email)
    else:
        # POST: send the verification email
        form = VerifyEmailForm()
        if form.validate():
            send_verification_email(form.email.data, form.challenge.data)

    return render_template('login_verify.html', form=form)
