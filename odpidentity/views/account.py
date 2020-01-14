from flask import Blueprint, redirect, request, abort, url_for, current_app, flash, render_template
from flask_mail import Message
from itsdangerous import BadData, JSONWebSignatureSerializer

from hydra import HydraAdminError
from odpaccounts.db import session as db_session
from odpaccounts.models.user import User

from .. import hydra_admin, mail
from ..lib import exceptions as x
from ..lib.hydra import hydra_error_page
from ..lib.users import validate_password_reset, update_user_password, update_user_verified
from ..forms.reset_password import ResetPasswordForm

bp = Blueprint('account', __name__)


@bp.route('/confirm-email')
def confirm_email():
    """
    This route is the target for email verification links. If the data received in the token
    is valid, then we conclude the login with Hydra.
    """
    verification_token = request.args.get('token', '')
    try:
        user, challenge = read_verification_token(verification_token)
        # call Hydra before updating the user; this will throw an error if the challenge is not valid for this user
        redirect_to = hydra_admin.accept_login_request(challenge, user.id)
        update_user_verified(user, True)
        flash("Your email address has been verified.")
        return redirect(redirect_to)

    except x.ODPIdentityError:
        abort(403)  # HTTP 403 Forbidden

    except HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/reset-password', methods=('GET', 'POST'))
def reset_password():
    """
    This route is the target for password reset links. If the data received in the token is
    valid, then we display a password reset form; if the subsequent post is valid, then we
    conclude the login with Hydra.
    """
    try:
        if request.method == 'GET':
            reset_token = request.args.get('token', '')
            user, challenge = read_password_reset_token(reset_token)
            form = ResetPasswordForm(challenge=challenge, email=user.email)
        else:
            # POST
            form = ResetPasswordForm()
            if form.validate():
                challenge = form.challenge.data
                email = form.email.data
                password = form.password.data
                try:
                    user = validate_password_reset(email, password)
                    # call Hydra before updating the password; this will throw an error if the challenge is not valid for this user
                    redirect_to = hydra_admin.accept_login_request(challenge, user.id)
                    update_user_password(user, password)
                    flash("Your password has been changed.")
                    return redirect(redirect_to)

                except x.ODPPasswordComplexityError:
                    form.password.errors.append("The password does not meet the minimum complexity requirements.")

        return render_template('reset_password.html', form=form,
                               password_complexity_description=current_app.config['PASSWORD_COMPLEXITY_DESCRIPTION'])

    except x.ODPIdentityError:
        abort(403)  # HTTP 403 Forbidden

    except HydraAdminError as e:
        return hydra_error_page(e)


def send_verification_email(email, challenge):
    """
    Send an email address verification email.

    :param email: the email address to be verified
    :param challenge: the Hydra login challenge
    """
    try:
        serializer = JSONWebSignatureSerializer(current_app.secret_key)
        verification_data = {
            'email': email,
            'challenge': challenge,
        }
        verification_token = serializer.dumps(verification_data)
        verification_url = url_for('account.confirm_email', token=verification_token, _external=True)
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


def read_verification_token(token):
    """
    Decode the token received in a verification link.

    :param token: email verification token
    :return: tuple(user, challenge)
    """
    try:
        serializer = JSONWebSignatureSerializer(current_app.secret_key)
        verification_data = serializer.loads(token)
        email = verification_data['email']
        challenge = verification_data['challenge']
        user = db_session.query(User).filter_by(email=email).one_or_none()
        if not user:
            raise x.ODPUserNotFound
        return user, challenge
    except BadData as e:
        raise x.ODPEmailVerificationError from e


def send_password_reset_email(email, challenge):
    """
    Send a password reset email.

    :param email: the email address
    :param challenge: the Hydra login challenge
    """
    try:
        serializer = JSONWebSignatureSerializer(current_app.secret_key)
        reset_data = {
            'email': email,
            'challenge': challenge,
        }
        reset_token = serializer.dumps(reset_data)
        reset_url = url_for('account.reset_password', token=reset_token, _external=True)
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


def read_password_reset_token(token):
    """
    Decode the token received in a password reset link.

    :param token: password reset token
    :return: tuple(user, challenge)
    """
    try:
        serializer = JSONWebSignatureSerializer(current_app.secret_key)
        reset_data = serializer.loads(token)
        email = reset_data['email']
        challenge = reset_data['challenge']
        user = db_session.query(User).filter_by(email=email).one_or_none()
        if not user:
            raise x.ODPUserNotFound
        return user, challenge
    except BadData as e:
        raise x.ODPEmailVerificationError from e
