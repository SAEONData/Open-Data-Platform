import re

import argon2
from argon2.exceptions import VerifyMismatchError

from odp.db.models.user import User
from odp.lib import exceptions as x

ph = argon2.PasswordHasher()


def validate_user_login(email, password):
    """
    Validate the credentials supplied by a user via the login form, returning the user object
    on success. An ``ODPIdentityError`` is raised if the login cannot be permitted for any reason.

    :param email: the input email address
    :param password: the input plain-text password
    :return: a User object

    :raises ODPUserNotFound: if the email address is not associated with any user account
    :raises ODPAccountLocked: if the user account has been temporarily locked
    :raises ODPIncorrectPassword: if the password is incorrect
    :raises ODPAccountDisabled: if the user account has been deactivated
    :raises ODPEmailNotVerified: if the email address has not yet been verified
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise x.ODPUserNotFound

    # first check whether the account is currently locked and should still be locked, unlocking it if necessary
    if is_account_locked(user):
        raise x.ODPAccountLocked

    # check the password before checking further account properties, to minimize the amount of knowledge
    # a potential attacker can gain about an account
    try:
        ph.verify(user.password, password)

        # if argon2_cffi's password hashing defaults have changed, we rehash the user's password
        if ph.check_needs_rehash(user.password):
            user.password = ph.hash(password)
            user.save()

    except VerifyMismatchError:
        if lock_account(user):
            raise x.ODPAccountLocked
        raise x.ODPIncorrectPassword

    if not user.active:
        raise x.ODPAccountDisabled

    if not user.verified:
        raise x.ODPEmailNotVerified

    return user


def validate_auto_login(user_id):
    """
    Validate a login request for which Hydra has indicated that the user is already authenticated,
    returning the user object on success. An ``ODPIdentityError`` is raised if the login cannot be
    permitted for any reason.

    :param user_id: the user id
    :return: a User object

    :raises ODPUserNotFound: if the user account associated with this id has been deleted
    :raises ODPAccountLocked: if the user account has been temporarily locked
    :raises ODPAccountDisabled: if the user account has been deactivated
    :raises ODPEmailNotVerified: if the user changed their email address since their last login,
        but have not yet verified it
    """
    user = User.query.get(user_id)
    if not user:
        raise x.ODPUserNotFound

    if is_account_locked(user):
        raise x.ODPAccountLocked

    if not user.active:
        raise x.ODPAccountDisabled

    if not user.verified:
        raise x.ODPEmailNotVerified

    return user


def is_account_locked(user):
    # todo...
    return False


def lock_account(user):
    # todo...
    return False


def validate_user_signup(email, password):
    """
    Validate the credentials supplied by a new user. An ``ODPIdentityError``
    is raised if the signup cannot be permitted for any reason.

    :param email: the input email address
    :param password: the input plain-text password

    :raises ODPEmailInUse: if the email address is already associated with a user account
    :raises ODPPasswordComplexityError: if the password does not meet the minimum complexity requirements
    """
    user = User.query.filter_by(email=email).first()
    if user:
        raise x.ODPEmailInUse

    if not check_password_complexity(email, password):
        raise x.ODPPasswordComplexityError


def validate_forgot_password(email):
    """
    Validate that a forgotten password request is for a valid email address.

    :param email: the input email address
    :return: a User object

    :raises ODPUserNotFound: if there is no user account for the given email address
    :raises ODPAccountLocked: if the user account has been temporarily locked
    :raises ODPAccountDisabled: if the user account has been deactivated
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise x.ODPUserNotFound

    if is_account_locked(user):
        raise x.ODPAccountLocked

    if not user.active:
        raise x.ODPAccountDisabled

    return user


def validate_password_reset(email, password):
    """
    Validate a new password set by the user.

    :param email: the user's email address
    :param password: the new password
    :return: a User object

    :raises ODPUserNotFound: if the email address is not associated with any user account
    :raises ODPPasswordComplexityError: if the password does not meet the minimum complexity requirements
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise x.ODPUserNotFound

    if not check_password_complexity(email, password):
        raise x.ODPPasswordComplexityError

    return user


def validate_email_verification(email):
    """
    Validate an email verification.

    :param email: the user's email address
    :return: a User object

    :raises ODPUserNotFound: if the email address is not associated with any user account
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        raise x.ODPUserNotFound

    return user


def create_user_account(email, password):
    """
    Create a new user account with the specified credentials. The password is hashed
    using the Argon2id algorithm.

    :param email: the input email address
    :param password: the input plain-text password
    :return: a User object
    """
    user = User(
        email=email,
        password=ph.hash(password),
        superuser=False,
        active=True,
        verified=False,
    )
    user.save()
    return user


def update_user_verified(user, verified):
    """
    Update the verified status of a user.

    :param user: a User instance
    :param verified: True/False
    """
    user.verified = verified
    user.save()


def update_user_password(user, password):
    """
    Update a user's password.

    :param user: a User instance
    :param password: the input plain-text password
    """
    user.password = ph.hash(password)
    user.save()


def check_password_complexity(email, password):
    """
    Check that a password meets the minimum complexity requirements,
    returning True if the requirements are satisfied, False otherwise.

    The rules are:
        - minimum length 10
        - at least one lowercase letter
        - at least one uppercase letter
        - at least one numeric character
        - at least one symbol character
        - a maximum of 3 consecutive characters from the email address

    :param email: the user's email address
    :param password: the input plain-text password
    :return: boolean
    """
    if len(password) < 10:
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'''[`~!@#$%^&*()\-=_+\[\]{}\\|;:'",.<>/?]''', password):
        return False
    for i in range(len(email) - 3):
        if email[i:(i + 4)] in password:
            return False

    return True
