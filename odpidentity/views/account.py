from flask import Blueprint, redirect, request, url_for, current_app, flash, render_template
from flask_mail import Message

from hydra import HydraAdminError

from . import hydra_error_page, encode_token, decode_token
from .. import hydra_admin, mail
from ..lib import exceptions as x
from ..lib.users import validate_password_reset, update_user_password, update_user_verified, validate_auto_login, validate_email_confirmation
from ..forms.reset_password import ResetPasswordForm

bp = Blueprint('account', __name__)


@bp.route('/confirm-email')
def confirm_email():
    """
    This route is the target for email verification links. The token ensures that it is only accessible
    from a verification email. If the token is valid, then we conclude the login with Hydra.
    """
    token = request.args.get('token')
    try:
        login_request, challenge, params = decode_token(token, 'account.confirm_email')

        email = params.get('email')
        try:
            user = validate_email_confirmation(email)
            update_user_verified(user, True)
            # todo send account verified email

            # we must still check that the user may log in
            validate_auto_login(user.id)
            redirect_to = hydra_admin.accept_login_request(challenge, user.id)

        except x.ODPIdentityError as e:
            # any validation error => reject login
            redirect_to = hydra_admin.reject_login_request(challenge, e.error_code, e.error_description)

        return redirect(redirect_to)

    except HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/reset-password', methods=('GET', 'POST'))
def reset_password():
    """
    This route is the target for password reset links. The token ensures that it is only accessible from a
    password reset email. If the token is valid, then we display a password reset form, and if the subsequent
    post is valid, then we conclude the login with Hydra.
    """
    token = request.args.get('token')
    try:
        login_request, challenge, params = decode_token(token, 'account.reset_password')

        form = ResetPasswordForm()
        email = params.get('email')

        if request.method == 'POST':
            if form.validate():
                password = form.password.data
                redirect_to = None
                try:
                    user = validate_password_reset(email, password)
                    update_user_password(user, password)
                    # todo send password updated email

                    # we must still check that the user may log in
                    validate_auto_login(user.id)
                    redirect_to = hydra_admin.accept_login_request(challenge, user.id)

                except x.ODPPasswordComplexityError:
                    form.password.errors.append("The password does not meet the minimum complexity requirements.")

                except x.ODPIdentityError as e:
                    # any other validation error => reject login
                    redirect_to = hydra_admin.reject_login_request(challenge, e.error_code, e.error_description)

                if redirect_to:
                    return redirect(redirect_to)

        return render_template('reset_password.html', form=form, token=token,
                               password_complexity_description=current_app.config['PASSWORD_COMPLEXITY_DESCRIPTION'])

    except HydraAdminError as e:
        return hydra_error_page(e)


def send_verification_email(email, challenge):
    """
    Send an email address verification email.

    :param email: the email address to be verified
    :param challenge: the Hydra login challenge
    """
    try:
        token = encode_token(challenge, 'account.confirm_email', email=email)
        verification_url = url_for('account.confirm_email', token=token, _external=True)
        msg = Message(
            subject="SAEON Open Data Platform: Please verify your email address",
            body="Click the following link to verify your email address: " + verification_url,
            sender=("SAEON", "noreply@saeon.ac.za"),
            recipients=[email],
        )
        mail.send(msg)
        flash("An email verification link has been sent to your email address.")
    except Exception as e:
        current_app.logger.error("Error sending verification email to {}: {}".format(email, e))
        flash("There was a problem sending the verification email.", category='error')


def send_password_reset_email(email, challenge):
    """
    Send a password reset email.

    :param email: the email address
    :param challenge: the Hydra login challenge
    """
    try:
        token = encode_token(challenge, 'account.reset_password', email=email)
        reset_url = url_for('account.reset_password', token=token, _external=True)
        msg = Message(
            subject="SAEON Open Data Platform: Request to reset your password",
            body="Click the following link to reset your password: " + reset_url,
            sender=("SAEON", "noreply@saeon.ac.za"),
            recipients=[email],
        )
        mail.send(msg)
        flash("A password reset link has been sent to your email address.")
    except Exception as e:
        current_app.logger.error("Error sending password reset email to {}: {}".format(email, e))
        flash("There was a problem sending the password reset email.", category='error')
