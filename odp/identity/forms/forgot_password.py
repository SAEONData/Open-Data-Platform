from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import input_required, email


class ForgotPasswordForm(FlaskForm):

    email = StringField(
        label='Email address',
        filters=[lambda s: s.lower() if s else s],
        validators=[input_required(), email()],
    )

    submit = SubmitField(
        label='Send reset link',
    )
