from flask_wtf import FlaskForm
from wtforms import SubmitField


class GoogleForm(FlaskForm):
    submit = SubmitField(
        label='Log in with Google',
    )
