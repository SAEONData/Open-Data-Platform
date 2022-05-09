from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Tag
from test.api import all_scopes, all_scopes_excluding, assert_forbidden
from test.factories import TagFactory


@pytest.fixture
def tag_batch():
    """Create and commit a batch of Tag instances."""
    return [TagFactory() for _ in range(randint(3, 5))]


def assert_db_state(tags):
    """Verify that the DB tag table contains the given tag batch."""
    Session.expire_all()
    result = Session.execute(select(Tag)).scalars().all()
    assert set((row.id, row.public, row.scope_id, row.scope_type, row.schema_id, row.schema_type) for row in result) \
           == set((tag.id, tag.public, tag.scope_id, tag.scope_type, tag.schema_id, tag.schema_type) for tag in tags)


def assert_json_result(response, json, tag):
    """Verify that the API result matches the given tag object."""
    assert response.status_code == 200
    assert json['id'] == tag.id
    assert json['public'] == tag.public
    assert json['scope_id'] == tag.scope_id
    assert json['schema_id'] == tag.schema_id
    assert json['schema_uri'] == tag.schema.uri
    assert json['schema_']['$id'] == tag.schema.uri


def assert_json_results(response, json, tags):
    """Verify that the API result list matches the given tag batch."""
    items = json['items']
    assert json['total'] == len(items) == len(tags)
    items.sort(key=lambda i: i['id'])
    tags.sort(key=lambda t: t.id)
    for n, tag in enumerate(tags):
        assert_json_result(response, items[n], tag)


@pytest.mark.parametrize('scopes', [
    [ODPScope.TAG_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.TAG_READ),
])
def test_list_tags(api, tag_batch, scopes):
    authorized = ODPScope.TAG_READ in scopes
    r = api(scopes).get('/tag/')
    if authorized:
        assert_json_results(r, r.json(), tag_batch)
    else:
        assert_forbidden(r)
    assert_db_state(tag_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.TAG_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.TAG_READ),
])
def test_get_tag(api, tag_batch, scopes):
    authorized = ODPScope.TAG_READ in scopes
    r = api(scopes).get(f'/tag/{tag_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), tag_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(tag_batch)
