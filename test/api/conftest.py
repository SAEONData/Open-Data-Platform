import pytest
from authlib.integrations.requests_client import OAuth2Session
from starlette.testclient import TestClient

import odp.api2
from test.factories import ClientFactory, ScopeFactory


@pytest.fixture
def api():
    def scoped_client(scopes):
        ClientFactory(
            id='odp.test',
            name='ODP Test Client',
            scopes=[ScopeFactory(id=s.value) for s in scopes],
        )
        token = OAuth2Session(
            client_id='odp.test',
            client_secret='secret',
            scope=' '.join(s.value for s in odp.ODPScope),
        ).fetch_token(
            'http://localhost:7444/oauth2/token',
            grant_type='client_credentials',
            timeout=0.1,
        )
        api_client = TestClient(app=odp.api2.app)
        api_client.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token['access_token'],
        }
        return api_client

    return scoped_client
