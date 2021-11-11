from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Catalogue
from test.api import assert_forbidden
from test.factories import CatalogueFactory


@pytest.fixture
def catalogue_batch():
    """Create and commit a batch of Catalogue instances."""
    return [CatalogueFactory() for _ in range(randint(3, 5))]


def assert_db_state(catalogues):
    """Verify that the DB catalogue table contains the given catalogue batch."""
    Session.expire_all()
    result = Session.execute(select(Catalogue)).scalars().all()
    assert set((row.id, row.schema_id, row.schema_type) for row in result) \
           == set((catalogue.id, catalogue.schema_id, catalogue.schema_type) for catalogue in catalogues)


def assert_json_result(response, json, catalogue):
    """Verify that the API result matches the given catalogue object."""
    assert response.status_code == 200
    assert json['id'] == catalogue.id
    assert json['schema_id'] == catalogue.schema_id


def assert_json_results(response, json, catalogues):
    """Verify that the API result list matches the given catalogue batch."""
    json.sort(key=lambda j: j['id'])
    catalogues.sort(key=lambda c: c.id)
    for n, catalogue in enumerate(catalogues):
        assert_json_result(response, json[n], catalogue)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.CATALOGUE_READ], True),
    ([ODPScope.TAG_READ], False),
    ([ODPScope.TAG_READ, ODPScope.CATALOGUE_READ], True),
])
def test_list_catalogues(api, catalogue_batch, scopes, authorized):
    r = api(scopes).get('/catalogue/')
    if authorized:
        assert_json_results(r, r.json(), catalogue_batch)
    else:
        assert_forbidden(r)
    assert_db_state(catalogue_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.CATALOGUE_READ], True),
    ([ODPScope.TAG_READ], False),
    ([ODPScope.TAG_READ, ODPScope.CATALOGUE_READ], True),
])
def test_get_catalogue(api, catalogue_batch, scopes, authorized):
    r = api(scopes).get(f'/catalogue/{catalogue_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), catalogue_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(catalogue_batch)
