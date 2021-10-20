import pytest
from starlette.testclient import TestClient

import odp.api2


@pytest.fixture
def api():
    with TestClient(app=odp.api2.app) as client:
        yield client
