class ODPIdentityError(Exception):
    """ Base exception class for identity service errors """

    # code and description are sent to Hydra when rejecting a login request
    error_code = 'unknown_error'
    error_description = "An unknown error occurred."


class ODPUserNotFound(ODPIdentityError):
    error_code = 'user_not_found'
    error_description = "The user id or email address is not associated with any user account."


class ODPEmailNotVerified(ODPIdentityError):
    error_code = 'email_not_verified'
    error_description = "The user's email address has not yet been verified."


class ODPIncorrectPassword(ODPIdentityError):
    error_code = 'incorrect_password'
    error_description = "The user has entered an incorrect password."


class ODPAccountDisabled(ODPIdentityError):
    error_code = 'account_disabled'
    error_description = "The user's account has been deactivated."


class ODPAccountLocked(ODPIdentityError):
    error_code = 'account_locked'
    error_description = "The user's account is temporarily locked."


class ODPEmailInUse(ODPIdentityError):
    error_code = 'email_in_use'
    error_description = "The email address is already associated with a user account."


class ODPPasswordComplexityError(ODPIdentityError):
    error_code = 'password_complexity'
    error_description = "The password does not meet the minimum complexity requirements."


class ODPSignupAuthenticatedUser(ODPIdentityError):
    error_code = 'signup_authenticated_user'
    error_description = "An authenticated user cannot sign up."
