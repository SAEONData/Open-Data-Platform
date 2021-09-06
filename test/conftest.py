import time

import docker
import pytest

from odp.config import config


@pytest.fixture(scope='session', autouse=True)
def database():
    client = docker.from_env()
    container = client.containers.run(
        'postgres:11',
        ports={5432: config.ODP.DB.PORT},
        environment=dict(
            PGDATA='/var/lib/postgresql/data',
            POSTGRES_DB=config.ODP.DB.NAME,
            POSTGRES_USER=config.ODP.DB.USER,
            POSTGRES_PASSWORD=config.ODP.DB.PASS,
        ),
        detach=True,
    )
    time.sleep(10)  # it takes 3-6 seconds for the DB to be ready
    try:
        import odp.db.models
        odp.db.Base.metadata.create_all(odp.db.engine)
        yield
    finally:
        container.remove(force=True)
