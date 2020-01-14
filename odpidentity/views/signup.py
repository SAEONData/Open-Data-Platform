from flask import Blueprint, render_template, redirect, url_for, request

from hydra import HydraAdminError

from .. import hydra_admin
from ..forms.credentials import CredentialsForm
from ..forms.verify_email import VerifyEmailForm
from ..lib import exceptions as x
from ..lib.hydra import hydra_error_page
from ..lib.users import create_user_account, validate_user_signup
from .account import send_verification_email

bp = Blueprint('signup', __name__)


@bp.route('/', methods=('GET', 'POST'))
def signup():
    try:
        try:
            if request.method == 'GET':
                challenge = request.args.get('challenge')
                login_request = hydra_admin.get_login_request(challenge)
                authenticated = login_request['skip']
                if authenticated:
                    raise x.ODPSignupLoggedInUser
                form = CredentialsForm(challenge=challenge)

            else:
                # it's a post from the user
                form = CredentialsForm()
                challenge = form.challenge.data
                if form.validate():
                    email = form.email.data
                    password = form.password.data
                    try:
                        validate_user_signup(email, password)
                        user = create_user_account(email, password)
                        send_verification_email(email, challenge)
                        return redirect(url_for('.verify', email=email, challenge=challenge))

                    except x.ODPEmailInUse:
                        form.email.errors.append("The email address is already associated with a user account.")

                    except x.ODPPasswordComplexityError:
                        form.password.errors.append("The password does not meet the minimum complexity requirements.")

            return render_template('signup.html', form=form)

        except x.ODPIdentityError as e:
            redirect_to = hydra_admin.reject_login_request(challenge, e.error_code, e.error_description)
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

    return render_template('signup_verify.html', form=form)
