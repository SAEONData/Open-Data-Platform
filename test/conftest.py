import time

import docker
import pytest
from sqlalchemy import text

import migrate.systemdata
import odp.db
from odp.config import config


@pytest.fixture(scope='session', autouse=True)
def database():
    """An auto-use, run-once fixture that provides a clean,
    containerized database with an up-to-date ODP schema."""
    client = docker.from_env()
    container = client.containers.run(
        'postgres:11',
        ports={5432: config.ODP.DB.PORT},
        environment=dict(
            PGDATA='/pgdata',
            POSTGRES_DB=config.ODP.DB.NAME,
            POSTGRES_USER=config.ODP.DB.USER,
            POSTGRES_PASSWORD=config.ODP.DB.PASS,
        ),
        detach=True,
    )
    time.sleep(8)  # it takes 3-6 seconds for the DB to be ready
    try:
        migrate.systemdata.create_schema()
        yield
    finally:
        container.remove(v=True, force=True)  # v => remove volumes


@pytest.fixture(autouse=True)
def session():
    """An auto-use, per-test fixture that disposes of the current
    session after every test."""
    try:
        yield
    finally:
        odp.db.Session.remove()


@pytest.fixture(autouse=True)
def delete_all_data():
    """An auto-use, per-test fixture that deletes all table data
    after every test."""
    try:
        yield
    finally:
        with odp.db.engine.begin() as conn:
            for table in odp.db.Base.metadata.tables:
                conn.execute(text(f'ALTER TABLE "{table}" DISABLE TRIGGER ALL'))
                conn.execute(text(f'DELETE FROM "{table}"'))
                conn.execute(text(f'ALTER TABLE "{table}" ENABLE TRIGGER ALL'))
