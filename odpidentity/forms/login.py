from wtforms import HiddenField

from .credentials import CredentialsForm
from ..lib.users import validate_user_login
from ..lib import exceptions as x


class LoginForm(CredentialsForm):

    login_challenge = HiddenField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None

    def validate(self):
        self.user_id = None
        if not super().validate():
            return False

        try:
            user = validate_user_login(self.email.data, self.password.data)
            self.user_id = user.id

        except x.ODPUserNotFound:
            self.email.errors.append("The email address is not associated with any user account.")
            return False

        except x.ODPAccountLocked:
            self.email.errors.append("The account is temporarily locked. Please try again later.")
            return False

        except x.ODPIncorrectPassword:
            self.password.errors.append("The email address and password do not match.")
            return False

        except x.ODPAccountDisabled:
            self.email.errors.append("The account is disabled.")
            return False

        except x.ODPEmailNotConfirmed:
            self.email.errors.append("The email address has not yet been verified.")
            return False

        return True
