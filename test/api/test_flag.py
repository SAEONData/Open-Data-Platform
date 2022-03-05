from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Flag
from test.api import assert_forbidden, all_scopes, all_scopes_excluding
from test.factories import FlagFactory


@pytest.fixture
def flag_batch():
    """Create and commit a batch of Flag instances."""
    return [FlagFactory() for _ in range(randint(3, 5))]


def assert_db_state(flags):
    """Verify that the DB flag table contains the given flag batch."""
    Session.expire_all()
    result = Session.execute(select(Flag)).scalars().all()
    assert set((row.id, row.public, row.scope_id, row.scope_type, row.schema_id, row.schema_type) for row in result) \
           == set((flag.id, flag.public, flag.scope_id, flag.scope_type, flag.schema_id, flag.schema_type) for flag in flags)


def assert_json_result(response, json, flag):
    """Verify that the API result matches the given flag object."""
    assert response.status_code == 200
    assert json['id'] == flag.id
    assert json['public'] == flag.public
    assert json['scope_id'] == flag.scope_id
    assert json['schema_id'] == flag.schema_id
    assert json['schema_uri'] == flag.schema.uri
    assert json['schema_']['$id'] == flag.schema.uri


def assert_json_results(response, json, flags):
    """Verify that the API result list matches the given flag batch."""
    items = json['items']
    assert json['total'] == len(items) == len(flags)
    items.sort(key=lambda i: i['id'])
    flags.sort(key=lambda f: f.id)
    for n, flag in enumerate(flags):
        assert_json_result(response, items[n], flag)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.FLAG_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.FLAG_READ), False),
])
def test_list_flags(api, flag_batch, scopes, authorized):
    r = api(scopes).get('/flag/')
    if authorized:
        assert_json_results(r, r.json(), flag_batch)
    else:
        assert_forbidden(r)
    assert_db_state(flag_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.FLAG_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.FLAG_READ), False),
])
def test_get_flag(api, flag_batch, scopes, authorized):
    r = api(scopes).get(f'/flag/{flag_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), flag_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(flag_batch)
