class ODPLoginError(Exception):
    """ Base class for any kind of login failure """

    # code and description are sent to Hydra when rejecting a login request
    error_code = 'login_error'
    error_description = "An unknown login error occurred."


class ODPUserNotFound(ODPLoginError):

    error_code = 'user_not_found'
    error_description = "The user id or email address is not associated with any user account."


class ODPEmailNotConfirmed(ODPLoginError):

    error_code = 'email_not_confirmed'
    error_description = "The user's email address has not yet been verified."


class ODPIncorrectPassword(ODPLoginError):

    error_code = 'incorrect_password'
    error_description = "The user has entered an incorrect password."


class ODPAccountDisabled(ODPLoginError):

    error_code = 'account_disabled'
    error_description = "The user's account has been deactivated."


class ODPAccountLocked(ODPLoginError):

    error_code = 'account_locked'
    error_description = "The user's account is temporarily locked."


class ODPUserRegistrationError(Exception):
    """ Base class for any kind of user registration error """


class ODPUserAlreadyExists(ODPUserRegistrationError):
    """ The email address is already associated with a user account """


class ODPPasswordComplexityError(ODPUserRegistrationError):
    """ The password does not meet the minimum complexity requirements """
