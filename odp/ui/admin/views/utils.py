from flask_login import current_user
from markupsafe import Markup

from odplib.ui import api


def get_tag_instance(obj, tag_id, user=False):
    """Get a single tag instance for a record or collection.

    The tag should have cardinality 'one' or 'user'; if 'user',
    set `user=True` to get the tag instance for the current user.
    """
    return next(
        (tag for tag in obj['tags'] if tag['tag_id'] == tag_id and (
            not user or tag['user_id'] == current_user.id
        )), None
    )


def get_tag_instances(obj, tag_id):
    """Get a page result of tag instances (with cardinality
    'user' or 'multi') for a record or collection."""
    return pagify(
        [tag for tag in obj['tags'] if tag['tag_id'] == tag_id]
    )


def pagify(item_list):
    """Convert a flat object list to a page result."""
    return {
        'items': item_list,
        'total': len(item_list),
        'page': 1,
        'pages': 1,
    }


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


def populate_vocabulary_term_choices(field, vocabulary_id, include_none=False):
    vocabulary = api.get(f'/vocabulary/{vocabulary_id}')
    field.choices = [('', '(None)')] if include_none else []
    field.choices += [
        (term['id'], term['id'])
        for term in vocabulary['terms']
    ]
