from flask_wtf import FlaskForm
from wtforms import SubmitField


class VerifyEmailForm(FlaskForm):
    submit = SubmitField(
        label='Re-send verification email',
    )
