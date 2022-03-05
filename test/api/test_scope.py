from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Scope
from test.api import assert_forbidden, all_scopes, all_scopes_excluding
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
    assert set((row.id, row.type) for row in result) \
           == set((scope.id, scope.type) for scope in scopes)


def assert_json_result(response, json, scope):
    """Verify that the API result matches the given scope object."""
    assert response.status_code == 200
    assert json['id'] == scope.id
    assert json['type'] == scope.type


def assert_json_results(response, json, scopes):
    """Verify that the API result list matches the given scope batch."""
    items = json['items']
    assert json['total'] == len(items) == len(scopes)
    items.sort(key=lambda i: i['id'])
    scopes.sort(key=lambda s: s.id)
    for n, scope in enumerate(scopes):
        assert_json_result(response, items[n], scope)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.SCOPE_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.SCOPE_READ), False),
])
def test_list_scopes(api, scope_batch, scopes, authorized):
    # add the parameterized scopes to the batch of expected scopes,
    # as they will be created by the api fixture
    scope_batch += [ScopeFactory.build(id=s.value, type='odp') for s in scopes]
    r = api(scopes).get('/scope/')
    if authorized:
        assert_json_results(r, r.json(), scope_batch)
    else:
        assert_forbidden(r)
    assert_db_state(scope_batch)
