from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import input_required, email


class ForgotPasswordForm(FlaskForm):

    challenge = HiddenField()

    email = StringField(
        label='Email address',
        filters=[lambda s: s.lower() if s else s],
        validators=[input_required(), email()],
    )
