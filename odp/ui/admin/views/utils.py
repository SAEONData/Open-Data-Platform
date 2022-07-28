from markupsafe import Markup

from odp.ui import api


def get_tag_instance(obj, tag_id):
    return next(
        (tag for tag in obj['tags'] if tag['tag_id'] == tag_id), None
    )


def populate_collection_choices(field, include_none=False):
    collections = api.get('/collection/')['items']
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (collection['id'], Markup(f"{collection['id']} &mdash; {collection['name']}"))
        for collection in collections
    ]


def populate_provider_choices(field, include_none=False):
    providers = api.get('/provider/')['items']
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (provider['id'], Markup(f"{provider['id']} &mdash; {provider['name']}"))
        for provider in providers
    ]


def populate_schema_choices(field, schema_type):
    schemas = api.get(f'/schema/?schema_type={schema_type}')['items']
    field.choices = [
        (schema['id'], schema['id'])
        for schema in schemas
    ]


def populate_scope_choices(field, scope_types=None):
    scopes = api.get('/scope/')['items']
    field.choices = [
        (scope['id'], scope['id'])
        for scope in scopes
        if scope_types is None or scope['type'] in scope_types
    ]


def populate_role_choices(field):
    roles = api.get('/role/')['items']
    field.choices = [
        (role['id'], role['id'])
        for role in roles
    ]
