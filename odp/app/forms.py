from flask import session
from wtforms import Form, StringField, SelectField
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


class ProviderForm(BaseForm):
    id = StringField(
        label='Provider id',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
    name = StringField(
        label='Provider name',
        validators=[
            input_required(),
            length(min=2),
        ],
    )


class CollectionForm(BaseForm):
    id = StringField(
        label='Collection id',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
    name = StringField(
        label='Collection name',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
    provider_id = SelectField(
        label='Provider',
    )
