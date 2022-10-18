from random import randint

import pytest
from sqlalchemy import select

from odplib.const import ODPScope
from odp.db import Session
from odp.db.models import SchemaType, Scope, ScopeType, Vocabulary, VocabularyTerm, VocabularyTermAudit
from test.api import (all_scopes, all_scopes_excluding, assert_conflict, assert_empty_result, assert_forbidden, assert_new_timestamp,
                      assert_not_found, assert_unprocessable)
from test.factories import SchemaFactory, VocabularyFactory, VocabularyTermFactory, fake


@pytest.fixture
def vocabulary_batch():
    """Create and commit a batch of Vocabulary instances,
    with associated terms."""
    return [VocabularyFactory() for _ in range(randint(3, 5))]


def prepare_project_vocabulary(vocab):
    """Update a factory-generated vocabulary to be an ODP Project vocabulary."""
    vocab.scope = Session.get(Scope, (ODPScope.VOCABULARY_PROJECT, ScopeType.odp)) or \
                  Scope(id=ODPScope.VOCABULARY_PROJECT, type=ScopeType.odp)
    vocab.schema = SchemaFactory(
        type=SchemaType.vocabulary,
        uri='https://odp.saeon.ac.za/schema/vocabulary/project',
    )
    vocab.save()
    Session.commit()
    return vocab


def term_ids(vocabulary):
    return tuple(sorted(term.term_id for term in vocabulary.terms))


def assert_db_state(vocabularies):
    """Verify that the DB vocabulary table contains the given vocabulary batch."""
    Session.expire_all()
    result = Session.execute(select(Vocabulary)).scalars().all()
    result.sort(key=lambda v: v.id)
    vocabularies.sort(key=lambda v: v.id)
    assert len(result) == len(vocabularies)
    for n, row in enumerate(result):
        assert row.id == vocabularies[n].id
        assert row.scope_id == vocabularies[n].scope_id
        assert row.scope_type == 'odp'
        assert row.schema_id == vocabularies[n].schema_id
        assert row.schema_type == 'vocabulary'
        dbterms = Session.execute(select(VocabularyTerm).where(VocabularyTerm.vocabulary_id == row.id)).scalars().all()
        dbterms.sort(key=lambda t: t.term_id)
        terms = sorted(vocabularies[n].terms, key=lambda t: t.term_id)
        assert len(dbterms) == len(terms)
        for m, trow in enumerate(dbterms):
            assert trow.vocabulary_id == terms[m].vocabulary_id == row.id
            assert trow.term_id == terms[m].term_id
            assert trow.data == terms[m].data


def assert_audit_log(command, term):
    """Verify that the vocabulary term audit table contains the given entry."""
    result = Session.execute(select(VocabularyTermAudit)).scalar_one_or_none()
    assert result.client_id == 'odp.test'
    assert result.user_id is None
    assert result.command == command
    assert_new_timestamp(result.timestamp)
    assert result._vocabulary_id == term.vocabulary.id
    assert result._term_id == term.term_id
    assert result._data == term.data | {'id': term.term_id}


def assert_no_audit_log():
    """Verify that no audit log entries have been created."""
    assert Session.execute(select(VocabularyTermAudit)).first() is None


def assert_json_result(response, json, vocabulary):
    """Verify that the API result matches the given vocabulary object."""
    assert response.status_code == 200
    assert json['id'] == vocabulary.id
    assert json['scope_id'] == vocabulary.scope_id
    assert json['schema_id'] == vocabulary.schema_id
    assert json['schema_uri'] == vocabulary.schema.uri
    assert json['schema_']['$id'] == vocabulary.schema.uri

    json_terms = sorted(json['terms'], key=lambda t: t['id'])
    vocab_terms = sorted(vocabulary.terms, key=lambda t: t.term_id)
    assert [(json_term['id'], json_term['data']) for json_term in json_terms] == \
           [(vocab_term.term_id, vocab_term.data) for vocab_term in vocab_terms]


def assert_json_results(response, json, vocabularies):
    """Verify that the API result list matches the given vocabulary batch."""
    items = json['items']
    assert json['total'] == len(items) == len(vocabularies)
    items.sort(key=lambda i: i['id'])
    vocabularies.sort(key=lambda v: v.id)
    for n, vocabulary in enumerate(vocabularies):
        assert_json_result(response, items[n], vocabulary)


@pytest.mark.parametrize('scopes', [
    [ODPScope.VOCABULARY_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.VOCABULARY_READ),
])
def test_list_vocabularies(api, vocabulary_batch, scopes):
    authorized = ODPScope.VOCABULARY_READ in scopes
    r = api(scopes).get('/vocabulary/')
    if authorized:
        assert_json_results(r, r.json(), vocabulary_batch)
    else:
        assert_forbidden(r)
    assert_db_state(vocabulary_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.VOCABULARY_READ],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.VOCABULARY_READ),
])
def test_get_vocabulary(api, vocabulary_batch, scopes):
    authorized = ODPScope.VOCABULARY_READ in scopes
    r = api(scopes).get(f'/vocabulary/{vocabulary_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), vocabulary_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(vocabulary_batch)


def test_get_vocabulary_not_found(api, vocabulary_batch):
    scopes = [ODPScope.VOCABULARY_READ]
    r = api(scopes).get('/vocabulary/foo')
    assert_not_found(r)
    assert_db_state(vocabulary_batch)


@pytest.mark.parametrize('scopes', [
    [ODPScope.VOCABULARY_PROJECT],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.VOCABULARY_PROJECT),
])
def test_create_term(api, vocabulary_batch, scopes):
    authorized = ODPScope.VOCABULARY_PROJECT in scopes
    client = api(scopes)

    modified_vocab_batch = vocabulary_batch.copy()
    modified_vocab = prepare_project_vocabulary(modified_vocab_batch[2])
    modified_vocab.terms += [term := VocabularyTermFactory.build(
        vocabulary=modified_vocab,
        data={'title': 'Some Project'},
    )]

    r = client.post(f'/vocabulary/{modified_vocab.id}/term', json=dict(
        id=term.term_id,
        data=term.data,
    ))

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_vocab_batch)
        assert_audit_log('insert', term)
    else:
        assert_forbidden(r)
        assert_db_state(vocabulary_batch)
        assert_no_audit_log()


def test_create_term_conflict(api, vocabulary_batch):
    scopes = [ODPScope.VOCABULARY_PROJECT]
    client = api(scopes)
    vocab = prepare_project_vocabulary(vocabulary_batch[2])
    r = client.post(f'/vocabulary/{vocab.id}/term', json=dict(
        id=vocab.terms[1].term_id,
        data={'title': 'Some Project'},
    ))
    assert_conflict(r, 'Term already exists in vocabulary')
    assert_db_state(vocabulary_batch)
    assert_no_audit_log()


def test_create_term_invalid(api, vocabulary_batch):
    scopes = [ODPScope.VOCABULARY_PROJECT]
    client = api(scopes)
    vocab = prepare_project_vocabulary(vocabulary_batch[2])
    r = client.post(f'/vocabulary/{vocab.id}/term', json=dict(
        id=fake.word(),
        data={'name': 'Project should have a title not a name'},
    ))
    assert_unprocessable(r, valid=False)
    assert_db_state(vocabulary_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes', [
    [ODPScope.VOCABULARY_PROJECT],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.VOCABULARY_PROJECT),
])
def test_update_term(api, vocabulary_batch, scopes):
    authorized = ODPScope.VOCABULARY_PROJECT in scopes
    client = api(scopes)

    modified_vocab_batch = vocabulary_batch.copy()
    modified_vocab = prepare_project_vocabulary(modified_vocab_batch[2])
    modified_vocab.terms[2] = (term := VocabularyTermFactory.build(
        vocabulary=modified_vocab,
        term_id=modified_vocab.terms[2].term_id,
        data={'title': 'Some Project'},
    ))

    r = client.put(f'/vocabulary/{modified_vocab.id}/term', json=dict(
        id=term.term_id,
        data=term.data,
    ))

    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_vocab_batch)
        assert_audit_log('update', term)
    else:
        assert_forbidden(r)
        assert_db_state(vocabulary_batch)
        assert_no_audit_log()


def test_update_term_not_found(api, vocabulary_batch):
    scopes = [ODPScope.VOCABULARY_PROJECT]
    client = api(scopes)
    vocab = prepare_project_vocabulary(vocabulary_batch[2])
    r = client.put(f'/vocabulary/{vocab.id}/term', json=dict(
        id=fake.word(),
        data={'title': 'Some Project'},
    ))
    assert_not_found(r)
    assert_db_state(vocabulary_batch)
    assert_no_audit_log()


def test_update_term_invalid(api, vocabulary_batch):
    scopes = [ODPScope.VOCABULARY_PROJECT]
    client = api(scopes)
    vocab = prepare_project_vocabulary(vocabulary_batch[2])
    r = client.put(f'/vocabulary/{vocab.id}/term', json=dict(
        id=vocab.terms[1].term_id,
        data={'name': 'Project should have a title not a name'},
    ))
    assert_unprocessable(r, valid=False)
    assert_db_state(vocabulary_batch)
    assert_no_audit_log()


@pytest.mark.parametrize('scopes', [
    [ODPScope.VOCABULARY_PROJECT],
    [],
    all_scopes,
    all_scopes_excluding(ODPScope.VOCABULARY_PROJECT),
])
def test_delete_term(api, vocabulary_batch, scopes):
    authorized = ODPScope.VOCABULARY_PROJECT in scopes
    client = api(scopes)

    modified_vocab_batch = vocabulary_batch.copy()
    modified_vocab = prepare_project_vocabulary(modified_vocab_batch[2])
    deleted_term = modified_vocab.terms[2]
    del modified_vocab.terms[2]

    r = client.delete(f'/vocabulary/{modified_vocab.id}/term/{deleted_term.term_id}')

    if authorized:
        assert_empty_result(r)
        # check audit log first because assert_db_state expires the deleted item
        assert_audit_log('delete', deleted_term)
        assert_db_state(modified_vocab_batch)
    else:
        assert_forbidden(r)
        assert_db_state(vocabulary_batch)
        assert_no_audit_log()


def test_delete_term_not_found(api, vocabulary_batch):
    scopes = [ODPScope.VOCABULARY_PROJECT]
    client = api(scopes)
    vocab = prepare_project_vocabulary(vocabulary_batch[2])
    r = client.delete(f'/vocabulary/{vocab.id}/term/{fake.word()}')
    assert_not_found(r)
    assert_db_state(vocabulary_batch)
    assert_no_audit_log()
