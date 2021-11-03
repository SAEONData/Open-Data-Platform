from flask import session
from wtforms import Form, StringField, SelectField, BooleanField, SelectMultipleField
from wtforms.csrf.session import SessionCSRF
from wtforms.validators import input_required, length
from wtforms.widgets import CheckboxInput, ListWidget


def init_app(app):
    BaseForm.Meta.csrf_secret = bytes(app.config['SECRET_KEY'], 'utf-8')


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF

        @property
        def csrf_context(self):
            return session


class ClientForm(BaseForm):
    id = StringField(
        label='Client id',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
    name = StringField(
        label='Client name',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
    scope_ids = MultiCheckboxField(
        label='Client scopes',
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
    collection_ids = MultiCheckboxField(
        label='Project collections',
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


class RoleForm(BaseForm):
    id = StringField(
        label='Role id',
        validators=[
            input_required(),
            length(min=2),
        ],
    )
    provider_id = SelectField(
        label='Provider',
    )
    scope_ids = MultiCheckboxField(
        label='Scopes',
    )


class ScopeForm(BaseForm):
    id = StringField(
        label='Scope id',
        validators=[
            input_required(),
            length(min=2),
        ],
    )


class UserForm(BaseForm):
    id = StringField(
        label='User id',
        render_kw=dict(readonly=''),
    )
    email = StringField(
        label='Email',
        render_kw=dict(readonly=''),
    )
    name = StringField(
        label='Name',
        render_kw=dict(readonly=''),
    )
    active = BooleanField(
        label='Active',
    )
