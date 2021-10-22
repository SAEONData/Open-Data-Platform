import pytest
from authlib.integrations.requests_client import OAuth2Session
from starlette.testclient import TestClient

import odp.api2


@pytest.fixture
def api():
    token = OAuth2Session(
        client_id='odp.test',
        client_secret='secret',
        scope=' '.join(s.value for s in odp.ODPScope),
    ).fetch_token(
        'http://localhost:7444/oauth2/token',
        grant_type='client_credentials',
        timeout=0.1,
    )
    with TestClient(app=odp.api2.app) as client:
        client.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token['access_token'],
        }
        yield client
