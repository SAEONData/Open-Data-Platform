from wtforms import HiddenField

from .credentials import CredentialsForm
from ..lib.users import validate_user_signup
from ..lib import exceptions as x


class SignupForm(CredentialsForm):

    challenge = HiddenField()

    def validate(self):
        if not super().validate():
            return False

        try:
            validate_user_signup(self.email.data, self.password.data)

        except x.ODPEmailInUse:
            self.email.errors.append("The email address is already associated with a user account.")
            return False

        except x.ODPPasswordComplexityError:
            self.password.errors.append("The password does not meet the minimum complexity requirements.")
            return False

        return True
