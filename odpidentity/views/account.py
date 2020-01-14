from flask import Blueprint, redirect, request, abort, url_for, current_app, flash
from flask_mail import Message
from itsdangerous import BadData, JSONWebSignatureSerializer

from hydra import HydraAdminError
from odpaccounts.db import session as db_session
from odpaccounts.models.user import User

from .. import hydra_admin, mail
from ..lib import exceptions as x
from ..lib.hydra import hydra_error_page

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
        redirect_to = hydra_admin.accept_login_request(challenge, user.id)

        user.verified = True
        db_session.add(user)
        db_session.commit()

        return redirect(redirect_to)

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
            subject="SAEON Open Data Platform - Please verify your email address",
            body="Click the following link to verify your email address: " + verification_url,
            sender="noreply@saeon.ac.za",
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
