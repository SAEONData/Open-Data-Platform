from flask_wtf import FlaskForm
from wtforms import SubmitField


class AutoLoginForm(FlaskForm):
    submit = SubmitField(
        label='Log in',
    )
