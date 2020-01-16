from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import input_required, email, equal_to


class SignupForm(FlaskForm):

    email = StringField(
        label='Email address',
        filters=[lambda s: s.lower() if s else s],
        validators=[input_required(), email()],
    )

    password = PasswordField(
        label='Password',
        validators=[input_required(), equal_to('confirm_password', "The passwords do not match")],
    )

    confirm_password = PasswordField(
        label='Confirm password',
        validators=[input_required()],
    )
