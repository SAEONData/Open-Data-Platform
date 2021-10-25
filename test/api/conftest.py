import pytest
from authlib.integrations.requests_client import OAuth2Session
from starlette.testclient import TestClient

import odp.api2
from odp.db.models import Scope, Client


@pytest.fixture(scope='session')
def api():
    client = Client(
        id='odp.test',
        name='Test Client',
        scopes=[Scope(id=s.value) for s in odp.ODPScope],
    )
    client.save()

    token = OAuth2Session(
        client_id='odp.test',
        client_secret='secret',
        scope=' '.join(s.value for s in odp.ODPScope),
    ).fetch_token(
        'http://localhost:7444/oauth2/token',
        grant_type='client_credentials',
        timeout=0.1,
    )
    with TestClient(app=odp.api2.app) as api_client:
        api_client.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token['access_token'],
        }
        yield api_client
