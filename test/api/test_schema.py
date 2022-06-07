from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Schema
from test.api import all_scopes, all_scopes_excluding, assert_forbidden, assert_not_found
from test.factories import SchemaFactory


@pytest.fixture
def schema_batch():
    """Create and commit a batch of Schema instances."""
    return [
        SchemaFactory()
        for _ in range(randint(3, 5))
    ]


def assert_db_state(schemas):
    """Verify that the DB schema table contains the given schema batch."""
    Session.expire_all()
    result = Session.execute(select(Schema)).scalars().all()
    assert set((row.id, row.type, row.uri) for row in result) \
           == set((schema.id, schema.type, schema.uri) for schema in schemas)


def assert_json_result(response, json, schema):
    """Verify that the API result matches the given schema object."""
    assert response.status_code == 200
    assert json['id'] == schema.id
    assert json['type'] == schema.type
    assert json['uri'] == schema.uri


def assert_json_results(response, json, schemas):
    """Verify that the API result list matches the given schema batch."""
    items = json['items']
    assert json['total'] == len(items) == len(schemas)
    items.sort(key=lambda i: i['id'])
    schemas.sort(key=lambda s: s.id)
    for n, schema in enumerate(schemas):
        assert_json_result(response, items[n], schema)


@pytest.mark.parametrize('scopes', [
    [ODPScope.SCHEMA_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.SCHEMA_READ),
])
def test_list_schemas(api, schema_batch, scopes):
    authorized = ODPScope.SCHEMA_READ in scopes
    r = api(scopes).get('/schema/')
    if authorized:
        assert_json_results(r, r.json(), schema_batch)
    else:
        assert_forbidden(r)
    assert_db_state(schema_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.SCHEMA_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.SCHEMA_READ),
])
def test_get_schema(api, schema_batch, scopes):
    authorized = ODPScope.SCHEMA_READ in scopes
    r = api(scopes).get(f'/schema/{schema_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), schema_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(schema_batch)


def test_get_schema_not_found(api, schema_batch):
    scopes = [ODPScope.SCHEMA_READ]
    r = api(scopes).get('/schema/foo')
    assert_not_found(r)
    assert_db_state(schema_batch)
