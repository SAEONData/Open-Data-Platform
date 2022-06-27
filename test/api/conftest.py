import os

import pytest
from authlib.integrations.requests_client import OAuth2Session
from starlette.testclient import TestClient

import odp.api
from odp.lib.hydra import HydraAdminAPI
from test.api import CollectionAuth
from test.factories import ClientFactory, ScopeFactory

hydra_admin_url = os.environ['HYDRA_ADMIN_URL']
hydra_public_url = os.environ['HYDRA_PUBLIC_URL']


@pytest.fixture
def api():
    def scoped_client(scopes, collection=None):
        ClientFactory(
            id='odp.test',
            scopes=[ScopeFactory(id=s.value, type='odp') for s in scopes],
            collection=collection,
        )
        token = OAuth2Session(
            client_id='odp.test',
            client_secret='secret',
            scope=' '.join(s.value for s in odp.ODPScope),
        ).fetch_token(
            f'{hydra_public_url}/oauth2/token',
            grant_type='client_credentials',
            timeout=1.0,
        )
        api_client = TestClient(app=odp.api.app)
        api_client.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token['access_token'],
        }
        return api_client

    return scoped_client


@pytest.fixture(scope='session')
def hydra_admin_api():
    return HydraAdminAPI(hydra_admin_url)


@pytest.fixture(params=CollectionAuth)
def collection_auth(request):
    """Use for parameterizing the three possible logic branches
    involving collection-specific authorization."""
    return request.param
