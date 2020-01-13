from wtforms import HiddenField
from flask_wtf import FlaskForm


class VerifyEmailForm(FlaskForm):

    challenge = HiddenField()
    email = HiddenField()
