import json

from flask import Flask, session
from wtforms import (
    Form,
    StringField,
    SelectField,
    BooleanField,
    SelectMultipleField,
    TextAreaField,
    ValidationError,
)
from wtforms.csrf.session import SessionCSRF
from wtforms.validators import input_required, length, regexp
from wtforms.widgets import CheckboxInput, ListWidget

from odp.api2.models import DOI_REGEX, SID_REGEX


def init_app(app: Flask):
    BaseForm.Meta.csrf_secret = bytes(app.config['SECRET_KEY'], 'utf-8')


def json_object(form, field):
    """A JSONTextField validator that ensures the value is a JSON object."""
    try:
        obj = json.loads(field.data)
        if not isinstance(obj, dict):
            raise ValidationError('The value must be a JSON object.')
    except json.JSONDecodeError:
        raise ValidationError('Invalid JSON')


class JSONTextField(TextAreaField):
    def process_data(self, value):
        self.data = json.dumps(value, indent=4, ensure_ascii=False)


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
        validators=[input_required(), length(min=2)],
    )
    name = StringField(
        label='Client name',
        validators=[input_required(), length(min=2)],
    )
    provider_id = SelectField(
        label='Provider',
    )
    scope_ids = MultiCheckboxField(
        label='Scopes',
    )


class CollectionForm(BaseForm):
    id = StringField(
        label='Collection id',
        validators=[input_required(), length(min=2)],
    )
    name = StringField(
        label='Collection name',
        validators=[input_required(), length(min=2)],
    )
    provider_id = SelectField(
        label='Provider',
    )


class ProjectForm(BaseForm):
    id = StringField(
        label='Project id',
        validators=[input_required(), length(min=2)],
    )
    name = StringField(
        label='Project name',
        validators=[input_required(), length(min=2)],
    )
    collection_ids = MultiCheckboxField(
        label='Collections',
    )


class ProviderForm(BaseForm):
    id = StringField(
        label='Provider id',
        validators=[input_required(), length(min=2)],
    )
    name = StringField(
        label='Provider name',
        validators=[input_required(), length(min=2)],
    )


class RecordForm(BaseForm):
    id = StringField(
        label='Record id',
        render_kw=dict(readonly=''),
    )
    doi = StringField(
        label='DOI (Digital Object Identifier)',
        validators=[regexp('^$|' + DOI_REGEX)],
    )
    sid = StringField(
        label='SID (Secondary Identifier)',
        validators=[regexp('^$|' + SID_REGEX)],
    )
    collection_id = SelectField(
        label='Collection',
    )
    schema_id = SelectField(
        label='Schema',
    )
    metadata = JSONTextField(
        label='Metadata',
        validators=[input_required(), json_object],
        render_kw={'rows': 24},
    )

    def validate_sid(self, field):
        if not self.doi.data and not field.data:
            raise ValidationError('SID is required if there is no DOI.')


class RecordTagQCForm(BaseForm):
    pass_ = BooleanField(
        label='Pass',
    )
    comment = StringField(
        label='Comment',
    )


class RoleForm(BaseForm):
    id = StringField(
        label='Role id',
        validators=[input_required(), length(min=2)],
    )
    provider_id = SelectField(
        label='Provider',
    )
    scope_ids = MultiCheckboxField(
        label='Scopes',
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
    role_ids = MultiCheckboxField(
        label='Roles',
    )
