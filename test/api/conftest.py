import pytest
from authlib.integrations.requests_client import OAuth2Session
from starlette.testclient import TestClient

import odp.api
from test.factories import ClientFactory, ScopeFactory


@pytest.fixture
def api():
    def scoped_client(scopes, provider=None):
        ClientFactory(
            id='odp.test',
            scopes=[ScopeFactory(id=s.value) for s in scopes],
            provider=provider,
        )
        token = OAuth2Session(
            client_id='odp.test',
            client_secret='secret',
            scope=' '.join(s.value for s in odp.ODPScope),
        ).fetch_token(
            'http://localhost:7444/oauth2/token',
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
