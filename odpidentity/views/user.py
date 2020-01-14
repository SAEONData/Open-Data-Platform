from flask import Blueprint, render_template, redirect, url_for, request, current_app, abort, flash
from flask_login import login_required
from flask_mail import Message
from itsdangerous import BadData, JSONWebSignatureSerializer

from hydra import HydraAdminError
from odpaccounts.db import session as db_session
from odpaccounts.models.user import User

from ..forms.credentials import CredentialsForm
from ..forms.verify_email import VerifyEmailForm
from ..lib.users import (
    create_user_account,
    validate_auto_login,
    validate_user_signup,
    validate_user_login,
)
from ..lib.hydra import hydra_error_page
from ..lib import exceptions as x
from . import hydra_admin, mail

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
                        return redirect(url_for('.verify_email', email=email, challenge=challenge))

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


@bp.route('/signup', methods=('GET', 'POST'))
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
                    user = db_session.query(User).filter_by(email=email).one_or_none()
                    if user:
                        # user exists: switch to a login
                        return login()
                    try:
                        validate_user_signup(email, password)
                        user = create_user_account(email, password)
                        send_verification_email(email, challenge)
                        return redirect(url_for('.verify_email', email=email, challenge=challenge))

                    except x.ODPPasswordComplexityError:
                        form.password.errors.append("The password does not meet the minimum complexity requirements.")

            return render_template('signup.html', form=form)

        except x.ODPIdentityError as e:
            redirect_to = hydra_admin.reject_login_request(challenge, e.error_code, e.error_description)
            return redirect(redirect_to)

    except HydraAdminError as e:
        return hydra_error_page(e)


@bp.route('/verify-email', methods=('GET', 'POST'))
def verify_email():
    if request.method == 'POST':
        # send the verification email
        form = VerifyEmailForm()
        if form.validate():
            send_verification_email(form.email.data, form.challenge.data)
    else:
        challenge = request.args.get('challenge')
        email = request.args.get('email')
        form = VerifyEmailForm(challenge=challenge, email=email)

    return render_template('verify_email.html', form=form)


@bp.route('/verified-email')
def verified_email():
    """
    This route is the target for email verification links. If the data received in the token
    is valid, then we conclude the login with Hydra.
    """
    verification_token = request.args.get('token')
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


@bp.route('/profile')
@login_required
def profile():
    return 'User profile page'


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
        verification_url = url_for('user.verified_email', token=verification_token, _external=True)
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
