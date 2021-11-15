from datetime import datetime, timedelta, timezone
from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Record, RecordAudit
from test.api import assert_empty_result, assert_forbidden
from test.factories import RecordFactory, CollectionFactory, SchemaFactory


@pytest.fixture
def record_batch():
    """Create and commit a batch of Record instances."""
    return [RecordFactory() for _ in range(randint(3, 5))]


def record_build(collection=None, **id):
    """Build and return an uncommitted Record instance.
    Referenced collection and schema are however committed."""
    return RecordFactory.build(
        **id,
        collection=collection or (collection := CollectionFactory()),
        collection_id=collection.id,
        schema=(schema := SchemaFactory(type='metadata')),
        schema_id=schema.id,
        schema_type=schema.type,
    )


def assert_db_state(records):
    """Verify that the DB record table contains the given record batch.
    Don't check metadata/validity as dicts are unhashable."""
    Session.expire_all()
    result = Session.execute(select(Record)).scalars().all()
    assert set((row.id, row.doi, row.sid, row.collection_id, row.schema_id, row.schema_type) for row in result) \
           == set((record.id, record.doi, record.sid, record.collection_id, record.schema_id, record.schema_type) for record in records)


def assert_audit_log(command, record=None, record_id=None):
    result = Session.execute(select(RecordAudit)).scalar_one_or_none()
    assert result.client_id == 'odp.test'
    assert result.user_id is None
    assert result.command == command
    assert datetime.now(timezone.utc) - timedelta(seconds=120) < result.timestamp < datetime.now(timezone.utc)
    if command in ('insert', 'update'):
        assert result._id == record.id
        assert result._doi == record.doi
        assert result._sid == record.sid
        assert result._metadata == record.metadata_
        assert result._collection_id == record.collection_id
        assert result._schema_id == record.schema_id
    elif command == 'delete':
        assert result._id == record_id
        assert result._doi is None
        assert result._sid is None
        assert result._metadata is None
        assert result._collection_id is None
        assert result._schema_id is None


def assert_no_audit_log():
    assert Session.execute(select(RecordAudit)).first() is None


def assert_json_result(response, json, record):
    """Verify that the API result matches the given record object."""
    assert response.status_code == 200
    assert json['id'] == record.id
    assert json['doi'] == record.doi
    assert json['sid'] == record.sid
    assert json['collection_id'] == record.collection_id
    assert json['schema_id'] == record.schema_id
    assert json['metadata'] == record.metadata_


def assert_json_results(response, json, records):
    """Verify that the API result list matches the given record batch."""
    json.sort(key=lambda j: j['id'])
    records.sort(key=lambda r: r.id)
    for n, record in enumerate(records):
        assert_json_result(response, json[n], record)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.RECORD_READ], True),
    ([ODPScope.RECORD_ADMIN], False),
    ([ODPScope.RECORD_ADMIN, ODPScope.RECORD_READ], True),
])
def test_list_records(api, record_batch, scopes, authorized):
    r = api(scopes).get('/record/')
    if authorized:
        assert_json_results(r, r.json(), record_batch)
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.RECORD_READ], True),
    ([ODPScope.RECORD_ADMIN], False),
    ([ODPScope.RECORD_ADMIN, ODPScope.RECORD_READ], True),
])
def test_list_records_with_provider_specific_api_client(api, record_batch, scopes, authorized):
    api_client_provider = record_batch[2].collection.provider
    r = api(scopes, api_client_provider).get('/record/')
    if authorized:
        assert_json_results(r, r.json(), [record_batch[2]])
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.RECORD_READ], True),
    ([ODPScope.RECORD_ADMIN], False),
    ([ODPScope.RECORD_ADMIN, ODPScope.RECORD_READ], True),
])
def test_get_record(api, record_batch, scopes, authorized):
    r = api(scopes).get(f'/record/{record_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), record_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([], False, False),
    ([ODPScope.RECORD_READ], False, False),
    ([ODPScope.RECORD_ADMIN], False, False),
    ([ODPScope.RECORD_ADMIN, ODPScope.RECORD_READ], False, False),
    ([], True, False),
    ([ODPScope.RECORD_READ], True, True),
    ([ODPScope.RECORD_ADMIN], True, False),
    ([ODPScope.RECORD_ADMIN, ODPScope.RECORD_READ], True, True),
])
def test_get_record_with_provider_specific_api_client(api, record_batch, scopes, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    r = api(scopes, api_client_provider).get(f'/record/{record_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), record_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.RECORD_READ], False),
    ([ODPScope.RECORD_CREATE], True),
    ([ODPScope.RECORD_CREATE, ODPScope.RECORD_READ], True),
])
def test_create_record(api, record_batch, scopes, authorized):
    modified_record_batch = record_batch + [record := record_build()]
    r = api(scopes).post('/record/', json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        record.id = r.json().get('id')
        assert_json_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('insert', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([], False, False),
    ([ODPScope.RECORD_READ], False, False),
    ([ODPScope.RECORD_CREATE], False, False),
    ([ODPScope.RECORD_CREATE, ODPScope.RECORD_READ], False, False),
    ([], True, False),
    ([ODPScope.RECORD_READ], True, False),
    ([ODPScope.RECORD_CREATE], True, True),
    ([ODPScope.RECORD_CREATE, ODPScope.RECORD_READ], True, True),
])
def test_create_record_with_provider_specific_api_client(api, record_batch, scopes, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    modified_record_batch = record_batch + [record := record_build(
        collection=record_batch[2].collection
    )]
    r = api(scopes, api_client_provider).post('/record/', json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        record.id = r.json().get('id')
        assert_json_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('insert', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.RECORD_READ], False),
    ([ODPScope.RECORD_MANAGE], True),
    ([ODPScope.RECORD_MANAGE, ODPScope.RECORD_READ], True),
])
def test_update_record(api, record_batch, scopes, authorized):
    modified_record_batch = record_batch.copy()
    modified_record_batch[2] = (record := record_build(
        id=record_batch[2].id
    ))
    r = api(scopes).put(f'/record/{record.id}', json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        assert_json_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('update', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([], False, False),
    ([ODPScope.RECORD_READ], False, False),
    ([ODPScope.RECORD_MANAGE], False, False),
    ([ODPScope.RECORD_MANAGE, ODPScope.RECORD_READ], False, False),
    ([], True, False),
    ([ODPScope.RECORD_READ], True, False),
    ([ODPScope.RECORD_MANAGE], True, True),
    ([ODPScope.RECORD_MANAGE, ODPScope.RECORD_READ], True, True),
])
def test_update_record_with_provider_specific_api_client(api, record_batch, scopes, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    modified_record_batch = record_batch.copy()
    modified_record_batch[2] = (record := record_build(
        id=record_batch[2].id,
        collection=record_batch[2].collection,
    ))
    r = api(scopes, api_client_provider).put(f'/record/{record.id}', json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        assert_json_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('update', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.RECORD_READ], False),
    ([ODPScope.RECORD_MANAGE], True),
    ([ODPScope.RECORD_MANAGE, ODPScope.RECORD_READ], True),
])
def test_delete_record(api, record_batch, scopes, authorized):
    modified_record_batch = record_batch.copy()
    del modified_record_batch[2]
    r = api(scopes).delete(f'/record/{(record_id := record_batch[2].id)}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_record_batch)
        assert_audit_log('delete', record_id=record_id)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([], False, False),
    ([ODPScope.RECORD_READ], False, False),
    ([ODPScope.RECORD_MANAGE], False, False),
    ([ODPScope.RECORD_MANAGE, ODPScope.RECORD_READ], False, False),
    ([], True, False),
    ([ODPScope.RECORD_READ], True, False),
    ([ODPScope.RECORD_MANAGE], True, True),
    ([ODPScope.RECORD_MANAGE, ODPScope.RECORD_READ], True, True),
])
def test_delete_record_with_provider_specific_api_client(api, record_batch, scopes, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    modified_record_batch = record_batch.copy()
    del modified_record_batch[2]
    r = api(scopes, api_client_provider).delete(f'/record/{(record_id := record_batch[2].id)}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_record_batch)
        assert_audit_log('delete', record_id=record_id)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()
