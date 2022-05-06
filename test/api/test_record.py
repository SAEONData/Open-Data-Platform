from datetime import datetime, timedelta, timezone
from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Record, RecordAudit, RecordFlag, RecordFlagAudit, RecordTag, RecordTagAudit, Scope, ScopeType
from test.api import all_scopes, all_scopes_excluding, assert_empty_result, assert_forbidden
from test.factories import CollectionFactory, FlagFactory, RecordFactory, SchemaFactory, TagFactory


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
    """Verify that the DB record table contains the given record batch."""
    Session.expire_all()
    result = Session.execute(select(Record)).scalars().all()
    result.sort(key=lambda r: r.id)
    records.sort(key=lambda r: r.id)
    assert len(result) == len(records)
    for n, row in enumerate(result):
        assert row.id == records[n].id
        assert row.doi == records[n].doi
        assert row.sid == records[n].sid
        assert row.metadata_ == records[n].metadata_
        assert row.timestamp < records[n].timestamp + timedelta(seconds=120)
        assert row.collection_id == records[n].collection_id
        assert row.schema_id == records[n].schema_id
        assert row.schema_type == records[n].schema_type


def assert_db_tag_state(record_id, record_tag):
    """Verify that the record_tag table contains the given record tag."""
    Session.expire_all()
    result = Session.execute(select(RecordTag)).scalar_one_or_none()
    if record_tag:
        assert result.record_id == record_id
        assert result.tag_id == record_tag['tag_id']
        assert result.user_id is None
        assert result.data == record_tag['data']
        assert datetime.now(timezone.utc) - timedelta(seconds=120) < result.timestamp < datetime.now(timezone.utc)
    else:
        assert result is None


def assert_db_flag_state(record_id, record_flag):
    """Verify that the record_flag table contains the given record flag."""
    Session.expire_all()
    result = Session.execute(select(RecordFlag)).scalar_one_or_none()
    if record_flag:
        assert result.record_id == record_id
        assert result.flag_id == record_flag['flag_id']
        assert result.user_id is None
        assert result.data == record_flag['data']
        assert datetime.now(timezone.utc) - timedelta(seconds=120) < result.timestamp < datetime.now(timezone.utc)
    else:
        assert result is None


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
    else:
        assert False


def assert_no_audit_log():
    assert Session.execute(select(RecordAudit)).first() is None


def assert_tag_audit_log(*entries):
    result = Session.execute(select(RecordTagAudit)).scalars().all()
    assert len(result) == len(entries)
    for n, row in enumerate(result):
        assert row.client_id == 'odp.test'
        assert row.user_id is None
        assert row.command == entries[n]['command']
        assert datetime.now(timezone.utc) - timedelta(seconds=120) < row.timestamp < datetime.now(timezone.utc)
        assert row._record_id == entries[n]['record_id']
        assert row._tag_id == entries[n]['record_tag']['tag_id']
        assert row._user_id is None
        if row.command in ('insert', 'update'):
            assert row._data == entries[n]['record_tag']['data']
        elif row.command == 'delete':
            assert row._data is None
        else:
            assert False


def assert_flag_audit_log(*entries):
    result = Session.execute(select(RecordFlagAudit)).scalars().all()
    assert len(result) == len(entries)
    for n, row in enumerate(result):
        assert row.client_id == 'odp.test'
        assert row.user_id is None
        assert row.command == entries[n]['command']
        assert datetime.now(timezone.utc) - timedelta(seconds=120) < row.timestamp < datetime.now(timezone.utc)
        assert row._record_id == entries[n]['record_id']
        assert row._flag_id == entries[n]['record_flag']['flag_id']
        assert row._user_id is None
        if row.command in ('insert', 'update'):
            assert row._data == entries[n]['record_flag']['data']
        elif row.command == 'delete':
            assert row._data is None
        else:
            assert False


def assert_json_record_result(response, json, record):
    """Verify that the API result matches the given record object."""
    assert response.status_code == 200
    assert json['id'] == record.id
    assert json['doi'] == record.doi
    assert json['sid'] == record.sid
    assert json['collection_id'] == record.collection_id
    assert json['schema_id'] == record.schema_id
    assert json['metadata'] == record.metadata_


def assert_json_tag_result(response, json, record_tag):
    """Verify that the API result matches the given record tag dict."""
    assert response.status_code == 200
    assert json['tag_id'] == record_tag['tag_id']
    assert json['user_id'] is None
    assert json['user_name'] is None
    assert json['data'] == record_tag['data']
    assert datetime.now(timezone.utc) - timedelta(seconds=120) < datetime.fromisoformat(json['timestamp']) < datetime.now(timezone.utc)


def assert_json_flag_result(response, json, record_flag):
    """Verify that the API result matches the given record flag dict."""
    assert response.status_code == 200
    assert json['flag_id'] == record_flag['flag_id']
    assert json['user_id'] is None
    assert json['user_name'] is None
    assert json['data'] == record_flag['data']
    assert datetime.now(timezone.utc) - timedelta(seconds=120) < datetime.fromisoformat(json['timestamp']) < datetime.now(timezone.utc)


def assert_json_record_results(response, json, records):
    """Verify that the API result list matches the given record batch."""
    items = json['items']
    assert json['total'] == len(items) == len(records)
    items.sort(key=lambda i: i['id'])
    records.sort(key=lambda r: r.id)
    for n, record in enumerate(records):
        assert_json_record_result(response, items[n], record)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.RECORD_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.RECORD_READ), False),
])
def test_list_records(api, record_batch, scopes, authorized):
    r = api(scopes).get('/record/')
    if authorized:
        assert_json_record_results(r, r.json(), record_batch)
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.RECORD_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.RECORD_READ), False),
])
def test_list_records_with_provider_specific_api_client(api, record_batch, scopes, authorized):
    api_client_provider = record_batch[2].collection.provider
    r = api(scopes, api_client_provider).get('/record/')
    if authorized:
        assert_json_record_results(r, r.json(), [record_batch[2]])
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.RECORD_READ], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.RECORD_READ), False),
])
def test_get_record(api, record_batch, scopes, authorized):
    r = api(scopes).get(f'/record/{record_batch[2].id}')
    if authorized:
        assert_json_record_result(r, r.json(), record_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes, matching_provider, authorized', [
    ([ODPScope.RECORD_READ], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes, False, False),
    (all_scopes_excluding(ODPScope.RECORD_READ), True, False),
])
def test_get_record_with_provider_specific_api_client(api, record_batch, scopes, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    r = api(scopes, api_client_provider).get(f'/record/{record_batch[2].id}')
    if authorized:
        assert_json_record_result(r, r.json(), record_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes, admin_route, authorized', [
    ([ODPScope.RECORD_WRITE], False, True),
    ([], False, False),
    (all_scopes, False, True),
    (all_scopes_excluding(ODPScope.RECORD_WRITE), False, False),
    ([ODPScope.RECORD_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes_excluding(ODPScope.RECORD_ADMIN), True, False),
])
def test_create_record(api, record_batch, scopes, admin_route, authorized):
    modified_record_batch = record_batch + [record := record_build()]
    route = '/record/admin/' if admin_route else '/record/'
    r = api(scopes).post(route, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        record.id = r.json().get('id')
        assert_json_record_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('insert', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, admin_route, matching_provider, authorized', [
    ([ODPScope.RECORD_WRITE], False, True, True),
    ([], False, True, False),
    (all_scopes, False, True, True),
    (all_scopes, False, False, False),
    (all_scopes_excluding(ODPScope.RECORD_WRITE), False, True, False),
    ([ODPScope.RECORD_ADMIN], True, True, True),
    ([], True, True, False),
    (all_scopes, True, True, True),
    (all_scopes, True, False, False),
    (all_scopes_excluding(ODPScope.RECORD_ADMIN), True, True, False),
])
def test_create_record_with_provider_specific_api_client(api, record_batch, scopes, admin_route, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    modified_record_batch = record_batch + [record := record_build(
        collection=record_batch[2].collection
    )]
    route = '/record/admin/' if admin_route else '/record/'
    r = api(scopes, api_client_provider).post(route, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        record.id = r.json().get('id')
        assert_json_record_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('insert', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, admin_route, authorized', [
    ([ODPScope.RECORD_WRITE], False, True),
    ([], False, False),
    (all_scopes, False, True),
    (all_scopes_excluding(ODPScope.RECORD_WRITE), False, False),
    ([ODPScope.RECORD_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes_excluding(ODPScope.RECORD_ADMIN), True, False),
])
def test_update_record(api, record_batch, scopes, admin_route, authorized):
    modified_record_batch = record_batch.copy()
    modified_record_batch[2] = (record := record_build(
        id=record_batch[2].id,
        doi=record_batch[2].doi,
    ))
    route = '/record/admin/' if admin_route else '/record/'
    r = api(scopes).put(route + record.id, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        assert_json_record_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('update', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, admin_route, matching_provider, authorized', [
    ([ODPScope.RECORD_WRITE], False, True, True),
    ([], False, True, False),
    (all_scopes, False, True, True),
    (all_scopes, False, False, False),
    (all_scopes_excluding(ODPScope.RECORD_WRITE), False, True, False),
    ([ODPScope.RECORD_ADMIN], True, True, True),
    ([], True, True, False),
    (all_scopes, True, True, True),
    (all_scopes, True, False, False),
    (all_scopes_excluding(ODPScope.RECORD_ADMIN), True, True, False),
])
def test_update_record_with_provider_specific_api_client(api, record_batch, scopes, admin_route, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    modified_record_batch = record_batch.copy()
    modified_record_batch[2] = (record := record_build(
        id=record_batch[2].id,
        doi=record_batch[2].doi,
        collection=record_batch[2].collection,
    ))
    route = '/record/admin/' if admin_route else '/record/'
    r = api(scopes, api_client_provider).put(route + record.id, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))
    if authorized:
        assert_json_record_result(r, r.json(), record)
        assert_db_state(modified_record_batch)
        assert_audit_log('update', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, admin_route, authorized', [
    ([ODPScope.RECORD_WRITE], False, True),
    ([], False, False),
    (all_scopes, False, True),
    (all_scopes_excluding(ODPScope.RECORD_WRITE), False, False),
    ([ODPScope.RECORD_ADMIN], True, True),
    ([], True, False),
    (all_scopes, True, True),
    (all_scopes_excluding(ODPScope.RECORD_ADMIN), True, False),
])
def test_delete_record(api, record_batch, scopes, admin_route, authorized):
    modified_record_batch = record_batch.copy()
    del modified_record_batch[2]
    route = '/record/admin/' if admin_route else '/record/'
    r = api(scopes).delete(f'{route}{(record_id := record_batch[2].id)}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_record_batch)
        assert_audit_log('delete', record_id=record_id)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, admin_route, matching_provider, authorized', [
    ([ODPScope.RECORD_WRITE], False, True, True),
    ([], False, True, False),
    (all_scopes, False, True, True),
    (all_scopes, False, False, False),
    (all_scopes_excluding(ODPScope.RECORD_WRITE), False, True, False),
    ([ODPScope.RECORD_ADMIN], True, True, True),
    ([], True, True, False),
    (all_scopes, True, True, True),
    (all_scopes, True, False, False),
    (all_scopes_excluding(ODPScope.RECORD_ADMIN), True, True, False),
])
def test_delete_record_with_provider_specific_api_client(api, record_batch, scopes, admin_route, matching_provider, authorized):
    api_client_provider = record_batch[2].collection.provider if matching_provider else record_batch[1].collection.provider
    modified_record_batch = record_batch.copy()
    del modified_record_batch[2]
    route = '/record/admin/' if admin_route else '/record/'
    r = api(scopes, api_client_provider).delete(f'{route}{(record_id := record_batch[2].id)}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_record_batch)
        assert_audit_log('delete', record_id=record_id)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.RECORD_TAG_QC], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.RECORD_TAG_QC), False),
])
def test_tag_record(api, record_batch, scopes, authorized):
    client = api(scopes)
    TagFactory(
        id='record-qc',
        type='record',
        scope=Session.get(
            Scope, (ODPScope.RECORD_TAG_QC, ScopeType.odp)
        ) or Scope(
            id=ODPScope.RECORD_TAG_QC, type=ScopeType.odp
        ),
        schema=SchemaFactory(
            type='tag',
            uri='https://odp.saeon.ac.za/schema/tag/record-qc',
        ),
    )

    # insert tag
    r = client.post(
        f'/record/{(record_id := record_batch[2].id)}/tag',
        json=(record_tag_v1 := dict(
            tag_id='record-qc',
            data={
                'pass_': (qc_passed := bool(randint(0, 1))),
            },
        )))
    if authorized:
        assert_json_tag_result(r, r.json(), record_tag_v1)
        assert_db_tag_state(record_id, record_tag_v1)
        assert_tag_audit_log(
            dict(command='insert', record_id=record_id, record_tag=record_tag_v1),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id, None)
        assert_tag_audit_log()
    assert_db_state(record_batch)
    assert_no_audit_log()

    # update tag
    r = client.post(
        f'/record/{record_id}/tag',
        json=(record_tag_v2 := dict(
            tag_id='record-qc',
            data={
                'pass_': not qc_passed,
                'comment': 'Hello',
            },
        )))
    if authorized:
        assert_json_tag_result(r, r.json(), record_tag_v2)
        assert_db_tag_state(record_id, record_tag_v2)
        assert_tag_audit_log(
            dict(command='insert', record_id=record_id, record_tag=record_tag_v1),
            dict(command='update', record_id=record_id, record_tag=record_tag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id, None)
        assert_tag_audit_log()
    assert_db_state(record_batch)
    assert_no_audit_log()

    # delete tag
    r = client.delete(f'/record/{record_id}/tag/{record_tag_v1["tag_id"]}')
    if authorized:
        assert_empty_result(r)
        assert_db_tag_state(record_id, None)
        assert_tag_audit_log(
            dict(command='insert', record_id=record_id, record_tag=record_tag_v1),
            dict(command='update', record_id=record_id, record_tag=record_tag_v2),
            dict(command='delete', record_id=record_id, record_tag=record_tag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id, None)
        assert_tag_audit_log()
    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.RECORD_FLAG_MIGRATED], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.RECORD_FLAG_MIGRATED), False),
])
def test_flag_record(api, record_batch, scopes, authorized):
    client = api(scopes)
    FlagFactory(
        id='record-migrated',
        type='record',
        scope=Session.get(
            Scope, (ODPScope.RECORD_FLAG_MIGRATED, ScopeType.odp)
        ) or Scope(
            id=ODPScope.RECORD_FLAG_MIGRATED, type=ScopeType.odp
        ),
        schema=SchemaFactory(
            type='flag',
            uri='https://odp.saeon.ac.za/schema/flag/record-migrated',
        ),
    )

    # insert flag
    r = client.post(
        f'/record/{(record_id := record_batch[2].id)}/flag',
        json=(record_flag_v1 := dict(
            flag_id='record-migrated',
            data={
                'published': True,
                'comment': 'Hello World',
            },
        )))
    if authorized:
        assert_json_flag_result(r, r.json(), record_flag_v1)
        assert_db_flag_state(record_id, record_flag_v1)
        assert_flag_audit_log(
            dict(command='insert', record_id=record_id, record_flag=record_flag_v1),
        )
    else:
        assert_forbidden(r)
        assert_db_flag_state(record_id, None)
        assert_flag_audit_log()
    assert_db_state(record_batch)

    # update flag
    r = client.post(
        f'/record/{record_id}/flag',
        json=(record_flag_v2 := dict(
            flag_id='record-migrated',
            data={
                'published': False,
            },
        )))
    if authorized:
        assert_json_flag_result(r, r.json(), record_flag_v2)
        assert_db_flag_state(record_id, record_flag_v2)
        assert_flag_audit_log(
            dict(command='insert', record_id=record_id, record_flag=record_flag_v1),
            dict(command='update', record_id=record_id, record_flag=record_flag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_flag_state(record_id, None)
        assert_flag_audit_log()
    assert_db_state(record_batch)

    # delete flag
    r = client.delete(f'/record/{record_id}/flag/{record_flag_v1["flag_id"]}')
    if authorized:
        assert_empty_result(r)
        assert_db_flag_state(record_id, None)
        assert_flag_audit_log(
            dict(command='insert', record_id=record_id, record_flag=record_flag_v1),
            dict(command='update', record_id=record_id, record_flag=record_flag_v2),
            dict(command='delete', record_id=record_id, record_flag=record_flag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_flag_state(record_id, None)
        assert_flag_audit_log()
    assert_db_state(record_batch)
