import time

import docker
import pytest
from sqlalchemy import text

import odp.db.models
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
        odp.db.Base.metadata.create_all(odp.db.engine)
        yield
    finally:
        container.remove(force=True)


@pytest.fixture(autouse=True)
def delete_all_data():
    try:
        yield
    finally:
        with odp.db.engine.begin() as conn:
            for table in odp.db.Base.metadata.tables:
                conn.execute(text(f'ALTER TABLE "{table}" DISABLE TRIGGER ALL'))
                conn.execute(text(f'DELETE FROM "{table}"'))
                conn.execute(text(f'ALTER TABLE "{table}" ENABLE TRIGGER ALL'))
