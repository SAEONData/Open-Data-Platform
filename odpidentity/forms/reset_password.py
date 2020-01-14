from flask_wtf import FlaskForm
from wtforms import PasswordField, HiddenField
from wtforms.validators import input_required, equal_to


class ResetPasswordForm(FlaskForm):

    challenge = HiddenField()
    email = HiddenField()

    password = PasswordField(
        label='New password',
        validators=[input_required(), equal_to('confirm_password', "The passwords do not match")],
    )

    confirm_password = PasswordField(
        label='Confirm password',
        validators=[input_required()],
    )
