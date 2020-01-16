from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import input_required, email


class LoginForm(FlaskForm):

    email = StringField(
        label='Email address',
        filters=[lambda s: s.lower() if s else s],
        validators=[input_required(), email()],
    )

    password = PasswordField(
        label='Password',
        validators=[input_required()],
    )
