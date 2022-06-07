from datetime import datetime
from random import randint

import pytest
from sqlalchemy import select

from odp import ODPCollectionTag, ODPScope
from odp.db import Session
from odp.db.models import CollectionTag, Record, RecordAudit, RecordTag, RecordTagAudit, Scope, ScopeType
from test.api import (ProviderAuth, all_scopes, all_scopes_excluding, assert_conflict, assert_empty_result, assert_forbidden, assert_new_timestamp,
                      assert_not_found, assert_unprocessable)
from test.factories import (CollectionFactory, CollectionTagFactory, ProjectFactory, ProviderFactory, RecordFactory, RecordTagFactory, SchemaFactory,
                            TagFactory)


@pytest.fixture
def record_batch():
    """Create and commit a batch of Record instances."""
    records = []
    for _ in range(randint(3, 5)):
        records += [record := RecordFactory()]
        for _ in range(randint(0, 3)):
            RecordTagFactory(record=record)
        for _ in range(randint(0, 3)):
            CollectionTagFactory(collection=record.collection)

    ProjectFactory.create_batch(randint(0, 3), collections=[
        record.collection for record in records
    ])
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
    assert len(result) == len(record_tags)
    for n, row in enumerate(result):
        assert row.record_id == record_id
        assert_new_timestamp(row.timestamp)
        try:
            # record_tags[n] is a dict we posted to the record API
            assert row.tag_id == record_tags[n]['tag_id']
            assert row.user_id is None
            assert row.data == record_tags[n]['data']
        except TypeError:
            # record_tags[n] is an object we created with RecordTagFactory
            assert row.tag_id == record_tags[n].tag_id
            assert row.user_id == record_tags[n].user_id
            assert row.data == record_tags[n].data


def assert_audit_log(command, record=None, record_id=None):
    result = Session.execute(select(RecordAudit)).scalar_one_or_none()
    assert result.client_id == 'odp.test'
    assert result.user_id is None
    assert result.command == command
    assert_new_timestamp(result.timestamp)
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
        assert_new_timestamp(row.timestamp)
        assert row._record_id == entries[n]['record_id']
        assert row._tag_id == entries[n]['record_tag']['tag_id']
        assert row._user_id is None
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
    assert json['provider_id'] == record.collection.provider_id
    assert json['collection_id'] == record.collection_id
    assert json['project_ids'] == [project.id for project in record.collection.projects]
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
    assert json['flag'] == record_tag['flag']
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
def test_list_records(api, record_batch, scopes, provider_auth):
    authorized = ODPScope.RECORD_READ in scopes

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch[2].collection.provider
        expected_result_batch = [record_batch[2]]
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = ProviderFactory()
        expected_result_batch = []
    else:
        api_client_provider = None
        expected_result_batch = record_batch

    r = api(scopes, api_client_provider).get('/record/')

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
def test_get_record(api, record_batch, scopes, provider_auth):
    authorized = ODPScope.RECORD_READ in scopes and \
                 provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch[2].collection.provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = record_batch[1].collection.provider
    else:
        api_client_provider = None

    r = api(scopes, api_client_provider).get(f'/record/{record_batch[2].id}')

    if authorized:
        assert_json_record_result(r, r.json(), record_batch[2])
    else:
        assert_forbidden(r)

    assert_db_state(record_batch)
    assert_no_audit_log()


def test_get_record_not_found(api, record_batch, provider_auth):
    scopes = [ODPScope.RECORD_READ]

    if provider_auth == ProviderAuth.NONE:
        api_client_provider = None
    else:
        api_client_provider = record_batch[2].collection.provider

    r = api(scopes, api_client_provider).get('/record/foo')

    assert_not_found(r)
    assert_db_state(record_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('admin_route, scopes, collection_tags', [
    (False, [ODPScope.RECORD_WRITE], []),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.ARCHIVE]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.PUBLISH]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH]),
    (False, [], []),
    (False, all_scopes, []),
    (False, all_scopes_excluding(ODPScope.RECORD_WRITE), []),
    (True, [ODPScope.RECORD_ADMIN], []),
    (True, [ODPScope.RECORD_ADMIN], [ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH]),
    (True, [], []),
    (True, all_scopes, []),
    (True, all_scopes_excluding(ODPScope.RECORD_ADMIN), []),
])
def test_create_record(api, record_batch, admin_route, scopes, collection_tags, provider_auth):
    route = '/record/admin/' if admin_route else '/record/'

    authorized = admin_route and ODPScope.RECORD_ADMIN in scopes or \
                 not admin_route and ODPScope.RECORD_WRITE in scopes
    authorized = authorized and provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch[2].collection.provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = record_batch[1].collection.provider
    else:
        api_client_provider = None

    if provider_auth in (ProviderAuth.MATCH, ProviderAuth.MISMATCH):
        new_record_collection = record_batch[2].collection
    else:
        new_record_collection = None  # new collection

    modified_record_batch = record_batch + [record := record_build(
        collection=new_record_collection,
        collection_tags=collection_tags,
    )]

    r = api(scopes, api_client_provider).post(route, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if not admin_route and ODPCollectionTag.ARCHIVE in collection_tags:
            assert_unprocessable(r, 'A record cannot be added to an archived collection')
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


def test_create_record_conflict(api, record_batch_with_ids, admin, provider_auth, conflict):
    route = '/record/admin/' if admin else '/record/'
    scopes = [ODPScope.RECORD_ADMIN] if admin else [ODPScope.RECORD_WRITE]
    authorized = provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch_with_ids[2].collection.provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = record_batch_with_ids[1].collection.provider
    else:
        api_client_provider = None

    if provider_auth in (ProviderAuth.MATCH, ProviderAuth.MISMATCH):
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

    r = api(scopes, api_client_provider).post(route, json=dict(
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
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.ARCHIVE]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.PUBLISH]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH]),
    (False, [], []),
    (False, all_scopes, []),
    (False, all_scopes_excluding(ODPScope.RECORD_WRITE), []),
    (True, [ODPScope.RECORD_ADMIN], []),
    (True, [ODPScope.RECORD_ADMIN], [ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH]),
    (True, [], []),
    (True, all_scopes, []),
    (True, all_scopes_excluding(ODPScope.RECORD_ADMIN), []),
])
def test_update_record(api, record_batch, admin_route, scopes, collection_tags, provider_auth):
    route = '/record/admin/' if admin_route else '/record/'

    authorized = admin_route and ODPScope.RECORD_ADMIN in scopes or \
                 not admin_route and ODPScope.RECORD_WRITE in scopes
    authorized = authorized and provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch[2].collection.provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = record_batch[1].collection.provider
    else:
        api_client_provider = None

    if provider_auth in (ProviderAuth.MATCH, ProviderAuth.MISMATCH):
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

    r = api(scopes, api_client_provider).put(route + record.id, json=dict(
        doi=record.doi,
        sid=record.sid,
        collection_id=record.collection_id,
        schema_id=record.schema_id,
        metadata=record.metadata_,
    ))

    if authorized:
        if not admin_route and set(collection_tags) & {ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH}:
            assert_unprocessable(r, 'Cannot update a record belonging to a published or archived collection')
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


@pytest.mark.parametrize('admin_route, scopes, collection_tags', [
    (False, [ODPScope.RECORD_WRITE], []),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.ARCHIVE]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.PUBLISH]),
    (False, [ODPScope.RECORD_WRITE], [ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH]),
    (False, [], []),
    (False, all_scopes, []),
    (False, all_scopes_excluding(ODPScope.RECORD_WRITE), []),
    (True, [ODPScope.RECORD_ADMIN], []),
    (True, [ODPScope.RECORD_ADMIN], [ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH]),
    (True, [], []),
    (True, all_scopes, []),
    (True, all_scopes_excluding(ODPScope.RECORD_ADMIN), []),
])
def test_delete_record(api, record_batch, admin_route, scopes, collection_tags, provider_auth):
    route = '/record/admin/' if admin_route else '/record/'

    authorized = admin_route and ODPScope.RECORD_ADMIN in scopes or \
                 not admin_route and ODPScope.RECORD_WRITE in scopes
    authorized = authorized and provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch[2].collection.provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = record_batch[1].collection.provider
    else:
        api_client_provider = None

    for ct in collection_tags:
        CollectionTagFactory(
            collection=record_batch[2].collection,
            tag=TagFactory(id=ct, type='collection'),
        )

    modified_record_batch = record_batch.copy()
    del modified_record_batch[2]

    r = api(scopes, api_client_provider).delete(f'{route}{(record_id := record_batch[2].id)}')

    if authorized:
        if not admin_route and set(collection_tags) & {ODPCollectionTag.ARCHIVE, ODPCollectionTag.PUBLISH}:
            assert_unprocessable(r, 'Cannot delete a record belonging to a published or archived collection')
            assert_db_state(record_batch)
            assert_no_audit_log()
        else:
            assert_empty_result(r)
            assert_db_state(modified_record_batch)
            assert_audit_log('delete', record_id=record_id)
    else:
        assert_forbidden(r)
        assert_db_state(record_batch)
        assert_no_audit_log()


@pytest.mark.parametrize('scopes', [
    [ODPScope.RECORD_TAG_QC],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.RECORD_TAG_QC),
])
def test_tag_record(api, record_batch_no_tags, scopes, provider_auth):
    authorized = ODPScope.RECORD_TAG_QC in scopes and \
                 provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch_no_tags[2].collection.provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = record_batch_no_tags[1].collection.provider
    else:
        api_client_provider = None

    client = api(scopes, api_client_provider)
    tag = TagFactory(
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
        f'/record/{(record_id := record_batch_no_tags[2].id)}/tag',
        json=(record_tag_v1 := dict(
            tag_id='record-qc',
            data={
                'pass_': (qc_passed := bool(randint(0, 1))),
            },
        )))
    if authorized:
        assert_json_tag_result(r, r.json(), record_tag_v1 | dict(flag=tag.flag, public=tag.public))
        assert_db_tag_state(record_id, record_tag_v1)
        assert_tag_audit_log(
            dict(command='insert', record_id=record_id, record_tag=record_tag_v1),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id)
        assert_tag_audit_log()
    assert_db_state(record_batch_no_tags)
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
        assert_json_tag_result(r, r.json(), record_tag_v2 | dict(flag=tag.flag, public=tag.public))
        assert_db_tag_state(record_id, record_tag_v2)
        assert_tag_audit_log(
            dict(command='insert', record_id=record_id, record_tag=record_tag_v1),
            dict(command='update', record_id=record_id, record_tag=record_tag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id)
        assert_tag_audit_log()
    assert_db_state(record_batch_no_tags)
    assert_no_audit_log()

    # delete tag
    r = client.delete(f'/record/{record_id}/tag/{record_tag_v1["tag_id"]}')
    if authorized:
        assert_empty_result(r)
        assert_db_tag_state(record_id)
        assert_tag_audit_log(
            dict(command='insert', record_id=record_id, record_tag=record_tag_v1),
            dict(command='update', record_id=record_id, record_tag=record_tag_v2),
            dict(command='delete', record_id=record_id, record_tag=record_tag_v2),
        )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id)
        assert_tag_audit_log()
    assert_db_state(record_batch_no_tags)
    assert_no_audit_log()


@pytest.fixture(params=[True, False])
def flag(request):
    return request.param


@pytest.mark.parametrize('scopes', [
    [ODPScope.RECORD_TAG_QC],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.RECORD_TAG_QC),
])
def test_tag_record_multi(api, record_batch_no_tags, scopes, provider_auth, flag):
    authorized = ODPScope.RECORD_TAG_QC in scopes and \
                 provider_auth in (ProviderAuth.NONE, ProviderAuth.MATCH)

    if provider_auth == ProviderAuth.MATCH:
        api_client_provider = record_batch_no_tags[2].collection.provider
    elif provider_auth == ProviderAuth.MISMATCH:
        api_client_provider = record_batch_no_tags[1].collection.provider
    else:
        api_client_provider = None

    client = api(scopes, api_client_provider)

    record_tag_1 = RecordTagFactory(
        record=record_batch_no_tags[2],
        tag=(tag := TagFactory(
            id='record-qc',
            type='record',
            flag=flag,
            scope=Session.get(
                Scope, (ODPScope.RECORD_TAG_QC, ScopeType.odp)
            ) or Scope(
                id=ODPScope.RECORD_TAG_QC, type=ScopeType.odp
            ),
            schema=SchemaFactory(
                type='tag',
                uri='https://odp.saeon.ac.za/schema/tag/generic',
            ),
        ))
    )

    r = client.post(
        f'/record/{(record_id := record_batch_no_tags[2].id)}/tag',
        json=(record_tag_2 := dict(
            tag_id='record-qc',
            data={'comment': 'Second tag instance'},
        )))

    if authorized:
        if flag:
            assert_conflict(r, 'Flag has already been set')
            assert_db_tag_state(record_id, record_tag_1)
            assert_tag_audit_log()
        else:
            assert_json_tag_result(r, r.json(), record_tag_2 | dict(flag=False, public=tag.public))
            assert_db_tag_state(record_id, record_tag_1, record_tag_2)
            assert_tag_audit_log(
                dict(command='insert', record_id=record_id, record_tag=record_tag_2),
            )
    else:
        assert_forbidden(r)
        assert_db_tag_state(record_id, record_tag_1)
        assert_tag_audit_log()

    assert_db_state(record_batch_no_tags)
