from flask import Flask
from wtforms import BooleanField, RadioField, SelectField, StringField, TextAreaField, ValidationError
from wtforms.validators import data_required, input_required, length, optional, regexp

from odp.lib.formats import DOI_REGEX, SID_REGEX
from odp.lib.hydra import GrantType, ResponseType, TokenEndpointAuthMethod
from odp.ui.forms import BaseForm, DateStringField, JSONTextField, MultiCheckboxField, StringListField, json_object


def init_app(app: Flask):
    BaseForm.init_app(app)


class ClientForm(BaseForm):
    id = StringField(
        label='Client id',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    name = StringField(
        label='Client name',
        validators=[data_required()],
    )
    secret = StringField(
        label='Client secret',
    )
    collection_id = SelectField(
        label='Collection',
    )
    scope_ids = MultiCheckboxField(
        label='Scope',
    )
    grant_types = MultiCheckboxField(
        label='Grant types',
        choices=[(gt.value, gt.value) for gt in GrantType],
    )
    response_types = MultiCheckboxField(
        label='Response types',
        choices=[(rt.value, rt.value) for rt in ResponseType],
    )
    redirect_uris = StringListField(
        label='Redirect URIs',
    )
    post_logout_redirect_uris = StringListField(
        label='Post-logout redirect URIs',
    )
    token_endpoint_auth_method = RadioField(
        label='Token endpoint auth method',
        choices=[(tm.value, tm.value) for tm in TokenEndpointAuthMethod],
        default=TokenEndpointAuthMethod.CLIENT_SECRET_BASIC.value,
    )
    allowed_cors_origins = StringListField(
        label='Allowed CORS origins',
    )

    def validate_secret(self, field):
        if field.data and len(field.data) < 16:
            raise ValidationError('Client secret must be at least 16 characters long.')

    def validate_scope_ids(self, field):
        if not field.data:
            raise ValidationError('At least one scope must be selected.')


class CollectionForm(BaseForm):
    id = StringField(
        label='Collection id',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    name = StringField(
        label='Collection name',
        validators=[data_required()],
    )
    provider_id = SelectField(
        label='Provider',
        validators=[input_required()],
    )
    doi_key = StringField(
        label='DOI key',
    )


class CollectionTagInfrastructureForm(BaseForm):
    infrastructure = SelectField(
        label='Infrastructure id',
        validators=[input_required()],
    )
    comment = StringField(
        label='Comment',
    )


class CollectionTagProjectForm(BaseForm):
    project = SelectField(
        label='Project id',
        validators=[input_required()],
    )
    comment = StringField(
        label='Comment',
    )


class ProviderForm(BaseForm):
    id = StringField(
        label='Provider id',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    name = StringField(
        label='Provider name',
        validators=[data_required()],
    )


class RecordForm(BaseForm):
    id = StringField(
        label='Record id',
        render_kw={'readonly': ''},
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
        validators=[input_required()],
    )
    schema_id = SelectField(
        label='Schema',
        validators=[input_required()],
    )
    metadata = JSONTextField(
        label='Metadata',
        validators=[input_required(), json_object],
        render_kw={'rows': 24},
    )

    def validate_sid(self, field):
        if not self.doi.data and not field.data:
            raise ValidationError('SID is required if there is no DOI.')


class RecordFilterForm(BaseForm):
    id_q = StringField(
        label='Search identifiers (Id, DOI and SID)',
    )
    title_q = StringField(
        label='Search titles',
    )
    collection = MultiCheckboxField(
        label='Filter by collection(s)',
    )


class RecordTagNoteForm(BaseForm):
    comment = TextAreaField(
        label='Note',
    )


class RecordTagQCForm(BaseForm):
    pass_ = BooleanField(
        label='Pass',
    )
    comment = StringField(
        label='Comment',
    )


class RecordTagEmbargoForm(BaseForm):
    start = DateStringField(
        label='Start date',
    )
    end = DateStringField(
        label='End date',
        validators=[optional()],
    )
    comment = StringField(
        label='Comment',
    )

    def validate_end(self, field):
        if self.start.data and field.data and field.data < self.start.data:
            raise ValidationError('The end date cannot be earlier than the start date.')


class RoleForm(BaseForm):
    id = StringField(
        label='Role id',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    collection_id = SelectField(
        label='Collection',
    )
    scope_ids = MultiCheckboxField(
        label='Scope',
    )


class UserForm(BaseForm):
    id = StringField(
        label='User id',
        render_kw={'readonly': ''},
    )
    email = StringField(
        label='Email',
        render_kw={'readonly': ''},
    )
    name = StringField(
        label='Name',
        render_kw={'readonly': ''},
    )
    active = BooleanField(
        label='Active',
    )
    role_ids = MultiCheckboxField(
        label='Roles',
    )


class VocabularyTermInfrastructureForm(BaseForm):
    id = StringField(
        label='Infrastructure id',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    name = StringField(
        label='Infrastructure name',
        validators=[data_required()],
    )
    description = StringField(
        label='Infrastructure description',
    )


class VocabularyTermProjectForm(BaseForm):
    id = StringField(
        label='Project id',
        filters=[lambda s: s.strip() if s else s],
        validators=[data_required(), length(min=2)],
    )
    title = StringField(
        label='Project title',
        validators=[data_required()],
    )
    description = StringField(
        label='Project description',
    )
