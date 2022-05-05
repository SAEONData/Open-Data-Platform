from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Catalog
from test.api import assert_forbidden, all_scopes, all_scopes_excluding
from test.factories import CatalogFactory


@pytest.fixture
def catalog_batch():
    """Create and commit a batch of Catalog instances."""
    return [CatalogFactory() for _ in range(randint(3, 5))]


def assert_db_state(catalogs):
    """Verify that the DB catalog table contains the given catalog batch."""
    Session.expire_all()
    result = Session.execute(select(Catalog)).scalars().all()
    assert set((row.id, row.schema_id, row.schema_type) for row in result) \
           == set((catalog.id, catalog.schema_id, catalog.schema_type) for catalog in catalogs)


def assert_json_result(response, json, catalog):
    """Verify that the API result matches the given catalog object."""
    assert response.status_code == 200
    assert json['id'] == catalog.id
    assert json['schema_id'] == catalog.schema_id


def assert_json_results(response, json, catalogs):
    """Verify that the API result list matches the given catalog batch."""
    items = json['items']
    assert json['total'] == len(items) == len(catalogs)
    items.sort(key=lambda i: i['id'])
    catalogs.sort(key=lambda c: c.id)
    for n, catalog in enumerate(catalogs):
        assert_json_result(response, items[n], catalog)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.CATALOG_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.CATALOG_READ), False),
])
def test_list_catalogs(api, catalog_batch, scopes, authorized):
    r = api(scopes).get('/catalog/')
    if authorized:
        assert_json_results(r, r.json(), catalog_batch)
    else:
        assert_forbidden(r)
    assert_db_state(catalog_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.CATALOG_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.CATALOG_READ), False),
])
def test_get_catalog(api, catalog_batch, scopes, authorized):
    r = api(scopes).get(f'/catalog/{catalog_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), catalog_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(catalog_batch)
