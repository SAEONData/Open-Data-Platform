from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Schema
from test.api import assert_forbidden
from test.factories import SchemaFactory


@pytest.fixture
def schema_batch():
    """Create and commit a batch of Schema instances.

    TODO: test other schema types; currently we only have metadata schema documents
    """
    return [
        SchemaFactory(type='metadata')
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
    json.sort(key=lambda j: j['id'])
    schemas.sort(key=lambda s: s.id)
    for n, schema in enumerate(schemas):
        assert_json_result(response, json[n], schema)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.SCHEMA_READ], True),
    ([ODPScope.TAG_READ], False),
    ([ODPScope.TAG_READ, ODPScope.SCHEMA_READ], True),
])
def test_list_schemas(api, schema_batch, scopes, authorized):
    r = api(scopes).get('/schema/')
    if authorized:
        assert_json_results(r, r.json(), schema_batch)
    else:
        assert_forbidden(r)
    assert_db_state(schema_batch)
