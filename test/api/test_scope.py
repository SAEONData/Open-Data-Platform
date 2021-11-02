from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Scope
from test.api import assert_forbidden
from test.factories import ScopeFactory


@pytest.fixture
def scope_batch():
    """Create and commit a batch of Scope instances."""
    return [
        ScopeFactory()
        for _ in range(randint(3, 5))
    ]


def assert_db_state(scopes):
    """Verify that the DB scope table contains the given scope batch."""
    Session.expire_all()
    result = Session.execute(select(Scope)).scalars().all()
    assert set(row.id for row in result) == set(scope.id for scope in scopes)


def assert_json_result(response, json, scope):
    """Verify that the API result matches the given scope object."""
    assert response.status_code == 200
    assert json['id'] == scope.id


def assert_json_results(response, json, scopes):
    """Verify that the API result list matches the given scope batch."""
    json.sort(key=lambda j: j['id'])
    scopes.sort(key=lambda p: p.id)
    for n, scope in enumerate(scopes):
        assert_json_result(response, json[n], scope)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.SCOPE_READ], True),
    ([ODPScope.TAG_READ], False),
    ([ODPScope.TAG_READ, ODPScope.SCOPE_READ], True),
])
def test_list_scopes(api, scope_batch, scopes, authorized):
    scope_batch += [ScopeFactory.build(id=s.value) for s in scopes]
    r = api(scopes).get('/scope/')
    if authorized:
        assert_json_results(r, r.json(), scope_batch)
    else:
        assert_forbidden(r)
    assert_db_state(scope_batch)
