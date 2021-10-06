import re
from typing import Optional

import argon2
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select

from odp.db import Session
from odp.db.models import User
from odp.lib import exceptions as x

ph = argon2.PasswordHasher()


def get_user_by_email(email: str) -> Optional[User]:
    return Session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()


def validate_user_login(email, password):
    """
    Validate the credentials supplied by a user via the login form, returning the user id
    on success. An ``ODPIdentityError`` is raised if the login cannot be permitted for any reason.

    :param email: the input email address
    :param password: the input plain-text password
    :return: the user id

    :raises ODPUserNotFound: if the email address is not associated with any user account
    :raises ODPAccountLocked: if the user account has been temporarily locked
    :raises ODPIncorrectPassword: if the password is incorrect
    :raises ODPAccountDisabled: if the user account has been deactivated
    :raises ODPEmailNotVerified: if the email address has not yet been verified
    """
    user = get_user_by_email(email)
    if not user:
        raise x.ODPUserNotFound

    # no password => either it's a non-human user (e.g. harvester),
    # or the user must be externally authenticated (e.g. via Google)
    if not user.password:
        raise x.ODPNoPassword

    # first check whether the account is currently locked and should still be locked, unlocking it if necessary
    if is_account_locked(user.id):
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
        if lock_account(user.id):
            raise x.ODPAccountLocked
        raise x.ODPIncorrectPassword

    if not user.active:
        raise x.ODPAccountDisabled

    if not user.verified:
        raise x.ODPEmailNotVerified

    return user.id


def validate_auto_login(user_id):
    """
    Validate a login request for which Hydra has indicated that the user is already authenticated,
    returning the user object on success. An ``ODPIdentityError`` is raised if the login cannot be
    permitted for any reason.

    :param user_id: the user id

    :raises ODPUserNotFound: if the user account associated with this id has been deleted
    :raises ODPAccountLocked: if the user account has been temporarily locked
    :raises ODPAccountDisabled: if the user account has been deactivated
    :raises ODPEmailNotVerified: if the user changed their email address since their last login,
        but have not yet verified it
    """
    user = Session.get(User, user_id)
    if not user:
        raise x.ODPUserNotFound

    if is_account_locked(user_id):
        raise x.ODPAccountLocked

    if not user.active:
        raise x.ODPAccountDisabled

    if not user.verified:
        raise x.ODPEmailNotVerified


def is_account_locked(user_id):
    # todo...
    return False


def lock_account(user_id):
    # todo...
    return False


def validate_forgot_password(email):
    """
    Validate that a forgotten password request is for a valid email address.

    :param email: the input email address
    :return: the user id

    :raises ODPUserNotFound: if there is no user account for the given email address
    :raises ODPAccountLocked: if the user account has been temporarily locked
    :raises ODPAccountDisabled: if the user account has been deactivated
    """
    user = get_user_by_email(email)
    if not user:
        raise x.ODPUserNotFound

    if is_account_locked(user.id):
        raise x.ODPAccountLocked

    if not user.active:
        raise x.ODPAccountDisabled

    return user.id


def validate_password_reset(email, password):
    """
    Validate a new password set by the user.

    :param email: the user's email address
    :param password: the new password
    :return: the user id

    :raises ODPUserNotFound: if the email address is not associated with any user account
    :raises ODPPasswordComplexityError: if the password does not meet the minimum complexity requirements
    """
    user = get_user_by_email(email)
    if not user:
        raise x.ODPUserNotFound

    if not check_password_complexity(email, password):
        raise x.ODPPasswordComplexityError

    return user.id


def validate_email_verification(email):
    """
    Validate an email verification.

    :param email: the user's email address
    :return: the user id

    :raises ODPUserNotFound: if the email address is not associated with any user account
    """
    user = get_user_by_email(email)
    if not user:
        raise x.ODPUserNotFound

    return user.id


def create_user_account(email, password=None, name=None):
    """
    Create a new user account with the specified credentials.
    Password may be omitted if the user is externally authenticated.
    A member record is created if the email domain matches an
    institutional domain. An ``ODPIdentityError`` is raised if
    the account cannot be created for any reason.

    The password, if supplied, is hashed using the Argon2id algorithm.

    :param email: the input email address
    :param password: (optional) the input plain-text password
    :param name: (optional) the user's personal name
    :return: the new user id

    :raises ODPEmailInUse: if the email address is already associated with a user account
    :raises ODPPasswordComplexityError: if the password does not meet the minimum complexity requirements
    """
    user = get_user_by_email(email)
    if user:
        raise x.ODPEmailInUse

    if password is not None and not check_password_complexity(email, password):
        raise x.ODPPasswordComplexityError

    user = User(
        email=email,
        password=ph.hash(password) if password else None,
        active=True,
        verified=False,
        name=name,
    )
    user.save()

    return user.id


def update_user_verified(user_id, verified):
    """
    Update the verified status of a user.

    :param user_id: the user id
    :param verified: True/False
    """
    user = Session.get(User, user_id)
    user.verified = verified
    user.save()


def update_user_password(user_id, password):
    """
    Update a user's password.

    :param user_id: the user id
    :param password: the input plain-text password
    """
    user = Session.get(User, user_id)
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


def password_complexity_description():
    return "The password must contain at least 10 characters, including 1 uppercase, " \
           "1 lowercase, 1 numeric, 1 symbol, and a maximum of 3 consecutive characters " \
           "from your email address."


def validate_google_login(email):
    """
    Validate a login completed via Google, returning the user id on success.
    An ``ODPIdentityError`` is raised if the login cannot be permitted for any reason.

    :param email: the Google email address

    :raises ODPUserNotFound: if there is no user account for the given email address
    :raises ODPAccountLocked: if the user account has been temporarily locked
    :raises ODPAccountDisabled: if the user account has been deactivated
    :raises ODPEmailNotVerified: if the email address has not been verified
    """
    user = get_user_by_email(email)
    if not user:
        raise x.ODPUserNotFound

    if is_account_locked(user.id):
        raise x.ODPAccountLocked

    if not user.active:
        raise x.ODPAccountDisabled

    return user.id


def update_user_profile(user_id, **userinfo):
    """
    Update optional user profile info.

    Only update user attributes that are supplied in the dict.

    :param user_id: the user id
    :param userinfo: dict containing profile info
    """
    user = Session.get(User, user_id)
    for attr in 'name', 'picture':
        if attr in userinfo:
            setattr(user, attr, userinfo[attr])
    user.save()


def get_user_profile(user_id):
    """
    Return a dict of user profile info.
    """
    user = Session.get(User, user_id)
    info = {}
    for attr in 'name', 'picture':
        info[attr] = getattr(user, attr)
    return info


def get_user_profile_by_email(email):
    """
    Return a dict of user profile info.
    """
    user = get_user_by_email(email)
    if not user:
        raise x.ODPUserNotFound

    return get_user_profile(user.id)
