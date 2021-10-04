from flask import session
from wtforms import Form, StringField
from wtforms.csrf.session import SessionCSRF
from wtforms.validators import input_required, length


def init_app(app):
    BaseForm.Meta.csrf_secret = bytes(app.config['SECRET_KEY'], 'utf-8')


class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF

        @property
        def csrf_context(self):
            return session


class ProjectForm(BaseForm):
    id = StringField(
        label='Project id',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
    name = StringField(
        label='Project name',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
