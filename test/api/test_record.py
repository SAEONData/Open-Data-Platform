import uuid
from datetime import datetime
from random import randint

import pytest
from sqlalchemy import select

from odp import ODPCollectionTag, ODPScope
from odp.db import Session
from odp.db.models import CollectionTag, PublishedDOI, Record, RecordAudit, RecordTag, RecordTagAudit, Scope, ScopeType
from test.api import (CollectionAuth, all_scopes, all_scopes_excluding, assert_conflict, assert_empty_result, assert_forbidden, assert_new_timestamp,
                      assert_not_found, assert_unprocessable)
from test.factories import CollectionFactory, CollectionTagFactory, RecordFactory, RecordTagFactory, SchemaFactory, TagFactory


@pytest.fixture
def record_batch():
    """Create and commit a batch of Record instances."""
    records = []
    for _ in range(randint(3, 5)):
        records += [record := RecordFactory()]
        RecordTagFactory.create_batch(randint(0, 3), record=record)
        CollectionTagFactory.create_batch(randint(0, 3), collection=record.collection)
    return records


@pytest.fixture
def record_batch_no_tags():
    """Create and commit a batch of Record instances
    without any tag instances."""
    return [RecordFactory() for _ in range(randint(3, 5))]


@pytest.fixture
def record_batch_with_ids():
    """Create and commit a batch of Record instances
    with both DOIs and SIDs."""
    return [RecordFactory(identifiers='both') for _ in range(randint(3, 5))]


def record_build(collection=None, collection_tags=None, **id):
    """Build and return an uncommitted Record instance.
    Referenced collection and schema are however committed."""
    record = RecordFactory.build(
        **id,
        collection=collection or (collection := CollectionFactory()),
        collection_id=collection.id,
        schema=(schema := SchemaFactory(type='metadata')),
        schema_id=schema.id,
        schema_type=schema.type,
    )
    if collection_tags:
        for ct in collection_tags:
            CollectionTagFactory(
                collection=record.collection,
                tag=TagFactory(id=ct, type='collection'),
            )
    return record


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
        assert_new_timestamp(row.timestamp)
        assert row.collection_id == records[n].collection_id
        assert row.schema_id == records[n].schema_id
        assert row.schema_type == records[n].schema_type


def assert_db_tag_state(record_id, *record_tags):
    """Verify that the record_tag table contains the given record tags."""
    Session.expire_all()
    result = Session.execute(select(RecordTag)).scalars().all()
    result.sort(key=lambda r: r.timestamp)

    assert len(result) == len(record_tags)
    for n, row in enumerate(result):
        assert row.record_id == record_id
        assert_new_timestamp(row.timestamp)
        if isinstance(record_tag := record_tags[n], RecordTag):
            assert row.tag_id == record_tag.tag_id
            assert row.user_id == record_tag.user_id
            assert row.data == record_tag.data
        else:
            assert row.tag_id == record_tag['tag_id']
            assert row.user_id is None
            assert row.data == record_tag['data']


def assert_audit_log(command, record):
    result = Session.execute(select(RecordAudit)).scalar_one_or_none()
    assert result.client_id == 'odp.test'
    assert result.user_id is None
    assert result.command == command
    assert_new_timestamp(result.timestamp)
    assert result._id == record.id
    assert result._doi == record.doi
    assert result._sid == record.sid
    assert result._metadata == record.metadata_
    assert result._collection_id == record.collection_id
    assert result._schema_id == record.schema_id


def assert_no_audit_log():
    assert Session.execute(select(RecordAudit)).first() is None


def assert_tag_audit_log(*entries):
    result = Session.execute(select(RecordTagAudit)).scalars().all()
    assert len(result) == len(entries)
    for n, row in enumerate(result):
        assert row.client_id == 'odp.test'
        assert row.user_id is None
        assert row.command == entries[n]['command']
        assert_new_timestamp(row.timestamp)
        assert row._record_id == entries[n]['record_id']
        assert row._tag_id == entries[n]['record_tag']['tag_id']
        assert row._user_id == entries[n]['record_tag'].get('user_id')
        if row.command in ('insert', 'update'):
            assert row._data == entries[n]['record_tag']['data']
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
    assert_new_timestamp(datetime.fromisoformat(json['timestamp']))

    json_tags = json['tags']
    db_tags = Session.execute(
        select(RecordTag).where(RecordTag.record_id == record.id)
    ).scalars().all() + Session.execute(
        select(CollectionTag).where(CollectionTag.collection_id == record.collection_id)
    ).scalars().all()
    assert len(json_tags) == len(db_tags)
    json_tags.sort(key=lambda t: t['tag_id'])
    db_tags.sort(key=lambda t: t.tag_id)
    for n, json_tag in enumerate(json_tags):
        assert json_tag['tag_id'] == db_tags[n].tag_id
        assert json_tag['user_id'] == db_tags[n].user_id
        assert json_tag['user_name'] == db_tags[n].user.name
        assert json_tag['data'] == db_tags[n].data
        assert_new_timestamp(datetime.fromisoformat(json_tag['timestamp']))


def assert_json_tag_result(response, json, record_tag):
    """Verify that the API result matches the given record tag dict."""
    assert response.status_code == 200
    assert json['tag_id'] == record_tag['tag_id']
    assert json['user_id'] is None
    assert json['user_name'] is None
    assert json['data'] == record_tag['data']
    assert_new_timestamp(datetime.fromisoformat(json['timestamp']))
    assert json['cardinality'] == record_tag['cardinality']
    assert json['public'] == record_tag['public']


def assert_json_record_results(response, json, records):
    """Verify that the API result list matches the given record batch."""
    items = json['items']
    assert json['total'] == len(items) == len(records)
    items.sort(key=lambda i: i['id'])
    records.sort(key=lambda r: r.id)
    for n, record in enumerate(records):
        assert_json_record_result(response, items[n], record)


@pytest.mark.parametrize('scopes', [
    [ODPScope.RECORD_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.RECORD_READ),
])
def test_list_records(api, record_batch, scopes, collection_auth):
    authorized = ODPScope.RECORD_READ in scopes

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch[2].collection
        expected_result_batch = [record_batch[2]]
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = CollectionFactory()
        expected_result_batch = []
    else:
        api_client_collection = None
        expected_result_batch = record_batch

    r = api(scopes, api_client_collection).get('/record/')

    if authorized:
        assert_json_record_results(r, r.json(), expected_result_batch)
    else:
        assert_forbidden(r)

    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes', [
    [ODPScope.RECORD_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.RECORD_READ),
])
def test_get_record(api, record_batch, scopes, collection_auth):
    authorized = ODPScope.RECORD_READ in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch[1].collection
    else:
        api_client_collection = None

    r = api(scopes, api_client_collection).get(f'/record/{record_batch[2].id}')

    if authorized:
        assert_json_record_result(r, r.json(), record_batch[2])
    else:
        assert_forbidden(r)

    assert_db_state(record_batch)
    assert_no_audit_log()


def test_get_record_not_found(api, record_batch, collection_auth):
    scopes = [ODPScope.RECORD_READ]

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = record_batch[2].collection

    r = api(scopes, api_client_collection).get('/record/foo')

    assert_not_found(r)
    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('admin_route, scopes, collection_tags', [
    (False, [ODPScope.RECORD_WRITE], []),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.FROZEN]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.READY]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.FROZEN, ODPCollectionTag.READY]),
    (False, [], []),
    (False, all_scopes, []),
    (False, all_scopes_excluding(ODPScope.RECORD_WRITE), []),
    (True, [ODPScope.RECORD_ADMIN], []),
    (True, [ODPScope.RECORD_ADMIN], [ODPCollectionTag.FROZEN, ODPCollectionTag.READY]),
    (True, [], []),
    (True, all_scopes, []),
    (True, all_scopes_excluding(ODPScope.RECORD_ADMIN), []),
])
def test_create_record(api, record_batch, admin_route, scopes, collection_tags, collection_auth):
    route = '/record/admin/' if admin_route else '/record/'

    authorized = admin_route and ODPScope.RECORD_ADMIN in scopes or \
                 not admin_route and ODPScope.RECORD_WRITE in scopes
    authorized = authorized and collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        new_record_collection = record_batch[2].collection
    else:
        new_record_collection = None  # new collection

    modified_record_batch = record_batch + [record := record_build(
        collection=new_record_collection,
        collection_tags=collection_tags,
    )]

    r = api(scopes, api_client_collection).post(route, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if not admin_route and ODPCollectionTag.FROZEN in collection_tags:
            assert_unprocessable(r, 'A record cannot be added to a frozen collection')
            assert_db_state(record_batch)
            assert_no_audit_log()
        else:
            record.id = r.json().get('id')
            assert_json_record_result(r, r.json(), record)
            assert_db_state(modified_record_batch)
            assert_audit_log('insert', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.fixture(params=[True, False])
def admin(request):
    return request.param


@pytest.fixture(params=['doi', 'sid', 'both'])
def conflict(request):
    return request.param


def test_create_record_conflict(api, record_batch_with_ids, admin, collection_auth, conflict):
    route = '/record/admin/' if admin else '/record/'
    scopes = [ODPScope.RECORD_ADMIN] if admin else [ODPScope.RECORD_WRITE]
    authorized = collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch_with_ids[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch_with_ids[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        new_record_collection = record_batch_with_ids[2].collection
    else:
        new_record_collection = None  # new collection

    if conflict == 'doi':
        record = record_build(
            doi=record_batch_with_ids[0].doi,
            collection=new_record_collection,
        )
    elif conflict == 'sid':
        record = record_build(
            sid=record_batch_with_ids[0].sid,
            collection=new_record_collection,
        )
    else:
        record = record_build(
            doi=record_batch_with_ids[0].doi,
            sid=record_batch_with_ids[1].sid,
            collection=new_record_collection,
        )

    r = api(scopes, api_client_collection).post(route, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if conflict in ('doi', 'both'):
            assert_conflict(r, 'DOI is already in use')
        else:
            assert_conflict(r, 'SID is already in use')
    else:
        assert_forbidden(r)

    assert_db_state(record_batch_with_ids)
    assert_no_audit_log()


@pytest.mark.parametrize('admin_route, scopes, collection_tags', [
    (False, [ODPScope.RECORD_WRITE], []),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.FROZEN]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.READY]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.FROZEN, ODPCollectionTag.READY]),
    (False, [], []),
    (False, all_scopes, []),
    (False, all_scopes_excluding(ODPScope.RECORD_WRITE), []),
    (True, [ODPScope.RECORD_ADMIN], []),
    (True, [ODPScope.RECORD_ADMIN], [ODPCollectionTag.FROZEN, ODPCollectionTag.READY]),
    (True, [], []),
    (True, all_scopes, []),
    (True, all_scopes_excluding(ODPScope.RECORD_ADMIN), []),
])
def test_update_record(api, record_batch, admin_route, scopes, collection_tags, collection_auth):
    route = '/record/admin/' if admin_route else '/record/'

    authorized = admin_route and ODPScope.RECORD_ADMIN in scopes or \
                 not admin_route and ODPScope.RECORD_WRITE in scopes
    authorized = authorized and collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        modified_record_collection = record_batch[2].collection
    else:
        modified_record_collection = None  # new collection

    modified_record_batch = record_batch.copy()
    modified_record_batch[2] = (record := record_build(
        id=record_batch[2].id,
        doi=record_batch[2].doi,
        collection=modified_record_collection,
        collection_tags=collection_tags,
    ))

    r = api(scopes, api_client_collection).put(route + record.id, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if not admin_route and set(collection_tags) & {ODPCollectionTag.FROZEN, ODPCollectionTag.READY}:
            assert_unprocessable(r, 'Cannot update a record belonging to a ready or frozen collection')
            assert_db_state(record_batch)
            assert_no_audit_log()
        else:
            assert_json_record_result(r, r.json(), record)
            assert_db_state(modified_record_batch)
            assert_audit_log('update', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


def test_update_record_not_found(api, record_batch, admin, collection_auth):
    # if not found on the admin route, the record is created!
    route = '/record/admin/' if admin else '/record/'
    scopes = [ODPScope.RECORD_ADMIN] if admin else [ODPScope.RECORD_WRITE]
    authorized = collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        modified_record_collection = record_batch[2].collection
    else:
        modified_record_collection = None  # new collection

    modified_record_batch = record_batch + [record := record_build(
        id=str(uuid.uuid4()),
        collection=modified_record_collection,
    )]

    r = api(scopes, api_client_collection).put(route + record.id, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if admin:
            assert_json_record_result(r, r.json(), record)
            assert_db_state(modified_record_batch)
            assert_audit_log('insert', record)
        else:
            assert_not_found(r)
            assert_db_state(record_batch)
            assert_no_audit_log()
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


def test_update_record_conflict(api, record_batch_with_ids, admin, collection_auth, conflict):
    route = '/record/admin/' if admin else '/record/'
    scopes = [ODPScope.RECORD_ADMIN] if admin else [ODPScope.RECORD_WRITE]
    authorized = collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch_with_ids[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch_with_ids[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        modified_record_collection = record_batch_with_ids[2].collection
    else:
        modified_record_collection = None  # new collection

    if conflict == 'doi':
        record = record_build(
            id=record_batch_with_ids[2].id,
            doi=record_batch_with_ids[0].doi,
            collection=modified_record_collection,
        )
    elif conflict == 'sid':
        record = record_build(
            id=record_batch_with_ids[2].id,
            sid=record_batch_with_ids[0].sid,
            collection=modified_record_collection,
        )
    else:
        record = record_build(
            id=record_batch_with_ids[2].id,
            doi=record_batch_with_ids[0].doi,
            sid=record_batch_with_ids[1].sid,
            collection=modified_record_collection,
        )

    r = api(scopes, api_client_collection).put(route + record.id, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if conflict in ('doi', 'both'):
            assert_conflict(r, 'DOI is already in use')
        else:
            assert_conflict(r, 'SID is already in use')
    else:
        assert_forbidden(r)

    assert_db_state(record_batch_with_ids)
    assert_no_audit_log()


@pytest.fixture(params=['change', 'remove'])
def doi_change(request):
    return request.param


@pytest.fixture(params=[True, False])
def published_doi(request):
    return request.param


def test_update_record_doi_change(api, record_batch_with_ids, admin, collection_auth, doi_change, published_doi):
    route = '/record/admin/' if admin else '/record/'
    scopes = [ODPScope.RECORD_ADMIN] if admin else [ODPScope.RECORD_WRITE]
    authorized = collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch_with_ids[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch_with_ids[1].collection
    else:
        api_client_collection = None

    if collection_auth in (CollectionAuth.MATCH, CollectionAuth.MISMATCH):
        modified_record_collection = record_batch_with_ids[2].collection
    else:
        modified_record_collection = None  # new collection

    if published_doi:
        PublishedDOI(doi=record_batch_with_ids[2].doi).save()

    modified_record_batch = record_batch_with_ids.copy()
    if doi_change == 'change':
        modified_record_batch[2] = (record := record_build(
            identifiers='doi',
            id=record_batch_with_ids[2].id,
            collection=modified_record_collection,
        ))
    elif doi_change == 'remove':
        modified_record_batch[2] = (record := record_build(
            identifiers='sid',
            id=record_batch_with_ids[2].id,
            collection=modified_record_collection,
        ))

    r = api(scopes, api_client_collection).put(route + record.id, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if published_doi:
            assert_unprocessable(r, 'The DOI has been published and cannot be modified.')
            assert_db_state(record_batch_with_ids)
            assert_no_audit_log()
        else:
            assert_json_record_result(r, r.json(), record)
            assert_db_state(modified_record_batch)
            assert_audit_log('update', record)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch_with_ids)
        assert_no_audit_log()


@pytest.mark.parametrize('admin_route, scopes, collection_tags', [
    (False, [ODPScope.RECORD_WRITE], []),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.FROZEN]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.READY]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.FROZEN, ODPCollectionTag.READY]),
    (False, [], []),
    (False, all_scopes, []),
    (False, all_scopes_excluding(ODPScope.RECORD_WRITE), []),
    (True, [ODPScope.RECORD_ADMIN], []),
    (True, [ODPScope.RECORD_ADMIN], [ODPCollectionTag.FROZEN, ODPCollectionTag.READY]),
    (True, [], []),
    (True, all_scopes, []),
    (True, all_scopes_excluding(ODPScope.RECORD_ADMIN), []),
])
def test_delete_record(api, record_batch_with_ids, admin_route, scopes, collection_tags, collection_auth, published_doi):
    route = '/record/admin/' if admin_route else '/record/'

    authorized = admin_route and ODPScope.RECORD_ADMIN in scopes or \
                 not admin_route and ODPScope.RECORD_WRITE in scopes
    authorized = authorized and collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch_with_ids[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch_with_ids[1].collection
    else:
        api_client_collection = None

    for ct in collection_tags:
        CollectionTagFactory(
            collection=record_batch_with_ids[2].collection,
            tag=TagFactory(id=ct, type='collection'),
        )

    if published_doi:
        PublishedDOI(doi=record_batch_with_ids[2].doi).save()

    modified_record_batch = record_batch_with_ids.copy()
    deleted_record = modified_record_batch[2]
    del modified_record_batch[2]

    r = api(scopes, api_client_collection).delete(f'{route}{(record_id := record_batch_with_ids[2].id)}')

    if authorized:
        if not admin_route and set(collection_tags) & {ODPCollectionTag.FROZEN, ODPCollectionTag.READY}:
            assert_unprocessable(r, 'Cannot delete a record belonging to a ready or frozen collection')
            assert_db_state(record_batch_with_ids)
            assert_no_audit_log()
        elif published_doi:
            assert_unprocessable(r, 'The DOI has been published and cannot be deleted.')
            assert_db_state(record_batch_with_ids)
            assert_no_audit_log()
        else:
            assert_empty_result(r)
            # check audit log first because assert_db_state expires the deleted item
            assert_audit_log('delete', deleted_record)
            assert_db_state(modified_record_batch)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch_with_ids)
        assert_no_audit_log()


def test_delete_record_not_found(api, record_batch, admin, collection_auth):
    route = '/record/admin/' if admin else '/record/'
    scopes = [ODPScope.RECORD_ADMIN] if admin else [ODPScope.RECORD_WRITE]

    if collection_auth == CollectionAuth.NONE:
        api_client_collection = None
    else:
        api_client_collection = record_batch[2].collection

    r = api(scopes, api_client_collection).delete(f'{route}foo')

    assert_not_found(r)
    assert_db_state(record_batch)
    assert_no_audit_log()


def new_generic_tag(cardinality):
    return TagFactory(
        type='record',
        cardinality=cardinality,
        scope=Session.get(
            Scope, (ODPScope.RECORD_QC, ScopeType.odp)
        ) or Scope(
            id=ODPScope.RECORD_QC, type=ScopeType.odp
        ),
        schema=SchemaFactory(
            type='tag',
            uri='https://odp.saeon.ac.za/schema/tag/generic',
        ),
    )


@pytest.mark.parametrize('scopes', [
    [ODPScope.RECORD_QC],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.RECORD_QC),
])
def test_tag_record(api, record_batch_no_tags, scopes, collection_auth, tag_cardinality):
    authorized = ODPScope.RECORD_QC in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch_no_tags[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch_no_tags[1].collection
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)
    tag = new_generic_tag(tag_cardinality)

    r = client.post(
        f'/record/{(record_id := record_batch_no_tags[2].id)}/tag',
        json=(record_tag_1 := dict(
            tag_id=tag.id,
            data={'comment': 'test1'},
        )))

    if authorized:
        assert_json_tag_result(r, r.json(), record_tag_1 | dict(cardinality=tag_cardinality, public=tag.public))
        assert_db_tag_state(record_id, record_tag_1)
        assert_tag_audit_log(
            dict(command='insert', record_id=record_id, record_tag=record_tag_1),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id)
        assert_tag_audit_log()

    r = client.post(
        f'/record/{(record_id := record_batch_no_tags[2].id)}/tag',
        json=(record_tag_2 := dict(
            tag_id=tag.id,
            data={'comment': 'test2'},
        )))

    if authorized:
        assert_json_tag_result(r, r.json(), record_tag_2 | dict(cardinality=tag_cardinality, public=tag.public))
        if tag_cardinality in ('one', 'user'):
            assert_db_tag_state(record_id, record_tag_2)
            assert_tag_audit_log(
                dict(command='insert', record_id=record_id, record_tag=record_tag_1),
                dict(command='update', record_id=record_id, record_tag=record_tag_2),
            )
        elif tag_cardinality == 'multi':
            assert_db_tag_state(record_id, record_tag_1, record_tag_2)
            assert_tag_audit_log(
                dict(command='insert', record_id=record_id, record_tag=record_tag_1),
                dict(command='insert', record_id=record_id, record_tag=record_tag_2),
            )
        else:
            assert False
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id)
        assert_tag_audit_log()

    assert_db_state(record_batch_no_tags)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes', [
    [ODPScope.RECORD_QC],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.RECORD_QC),
])
def test_tag_record_user_conflict(api, record_batch_no_tags, scopes, collection_auth, tag_cardinality):
    authorized = ODPScope.RECORD_QC in scopes and \
                 collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch_no_tags[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch_no_tags[1].collection
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)
    tag = new_generic_tag(tag_cardinality)
    record_tag_1 = RecordTagFactory(
        record=record_batch_no_tags[2],
        tag=tag,
    )

    r = client.post(
        f'/record/{(record_id := record_batch_no_tags[2].id)}/tag',
        json=(record_tag_2 := dict(
            tag_id=tag.id,
            data={'comment': 'test2'},
        )))

    if authorized:
        if tag_cardinality == 'one':
            assert_conflict(r, 'Cannot update a tag set by another user')
            assert_db_tag_state(record_id, record_tag_1)
            assert_tag_audit_log()
        elif tag_cardinality in ('user', 'multi'):
            assert_json_tag_result(r, r.json(), record_tag_2 | dict(cardinality=tag_cardinality, public=tag.public))
            assert_db_tag_state(record_id, record_tag_1, record_tag_2)
            assert_tag_audit_log(
                dict(command='insert', record_id=record_id, record_tag=record_tag_2),
            )
        else:
            assert False
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id, record_tag_1)
        assert_tag_audit_log()

    assert_db_state(record_batch_no_tags)
    assert_no_audit_log()


@pytest.fixture(params=[True, False])
def same_user(request):
    return request.param


@pytest.mark.parametrize('admin_route, scopes', [
    (False, [ODPScope.RECORD_QC]),
    (False, []),
    (False, all_scopes),
    (False, all_scopes_excluding(ODPScope.RECORD_QC)),
    (True, [ODPScope.RECORD_ADMIN]),
    (True, []),
    (True, all_scopes),
    (True, all_scopes_excluding(ODPScope.RECORD_ADMIN)),
])
def test_untag_record(api, record_batch_no_tags, admin_route, scopes, collection_auth, tag_cardinality, same_user):
    route = '/record/admin/' if admin_route else '/record/'

    authorized = admin_route and ODPScope.RECORD_ADMIN in scopes or \
                 not admin_route and ODPScope.RECORD_QC in scopes
    authorized = authorized and collection_auth in (CollectionAuth.NONE, CollectionAuth.MATCH)

    if collection_auth == CollectionAuth.MATCH:
        api_client_collection = record_batch_no_tags[2].collection
    elif collection_auth == CollectionAuth.MISMATCH:
        api_client_collection = record_batch_no_tags[1].collection
    else:
        api_client_collection = None

    client = api(scopes, api_client_collection)
    record = record_batch_no_tags[2]
    record_tags = RecordTagFactory.create_batch(randint(1, 3), record=record)

    tag = new_generic_tag(tag_cardinality)
    if same_user:
        record_tag_1 = RecordTagFactory(
            record=record,
            tag=tag,
            user=None,
        )
    else:
        record_tag_1 = RecordTagFactory(
            record=record,
            tag=tag,
        )
    record_tag_1_dict = {
        'tag_id': record_tag_1.tag_id,
        'user_id': record_tag_1.user_id,
        'data': record_tag_1.data,
    }

    r = client.delete(f'{route}{record.id}/tag/{record_tag_1.id}')

    if authorized:
        if not admin_route and not same_user:
            assert_forbidden(r)
            assert_db_tag_state(record.id, *record_tags, record_tag_1)
            assert_tag_audit_log()
        else:
            assert_empty_result(r)
            assert_db_tag_state(record.id, *record_tags)
            assert_tag_audit_log(
                dict(command='delete', record_id=record.id, record_tag=record_tag_1_dict),
            )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record.id, *record_tags, record_tag_1)
        assert_tag_audit_log()

    assert_db_state(record_batch_no_tags)
    assert_no_audit_log()
