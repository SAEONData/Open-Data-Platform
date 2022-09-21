import pytest
from jschon import JSON, JSONPatch, JSONSchemaError, URI

from odp.lib.schema import schema_catalog as catalog
from test.factories import VocabularyFactory


def test_validity():
    with catalog.session() as session:
        input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115'), session=session)
        input_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115-example'))
        output_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/saeon/datacite-4'), session=session)
        output_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/datacite-4-example-translated'))

        assert input_schema.validate().valid
        assert input_schema.evaluate(JSON(input_json)).valid
        assert output_schema.validate().valid
        assert output_schema.evaluate(JSON(output_json)).valid


def test_translate_iso19115_to_datacite():
    with catalog.session() as session:
        input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115'), session=session)
        input_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115-example'))
        output_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/datacite-4-example-translated'))

        result = input_schema.evaluate(JSON(input_json))
        patch = result.output('translation-patch', scheme='saeon/datacite-4')
        translation = result.output('translation', scheme='saeon/datacite-4')

        assert JSONPatch(*patch).evaluate(None) == translation

        translation = result.output('translation', scheme='saeon/datacite-4', clear_empties=True)

        assert translation == output_json


@pytest.mark.parametrize('vocab_id', ['Project', 'Infrastructure'])
def test_vocabulary_keyword_valid_term(vocab_id):
    with catalog.session() as session:
        vocab_key = vocab_id.lower()
        vocab = VocabularyFactory(id=vocab_id)
        tag_schema = catalog.get_schema(URI(f'https://odp.saeon.ac.za/schema/tag/collection/{vocab_key}'), session=session)
        tag_json = JSON({
            vocab_key: vocab.terms[0].term_id
        })
        assert (result := tag_schema.evaluate(tag_json)).valid
        annotation = next(
            ann for ann in result.output('basic')['annotations']
            if ann['instanceLocation'] == f'/{vocab_key}'
        )
        assert annotation['annotation'] == vocab_id


@pytest.mark.parametrize('vocab_id', ['Project', 'Infrastructure'])
def test_vocabulary_keyword_invalid_term(vocab_id):
    with catalog.session() as session:
        vocab_key = vocab_id.lower()
        vocab = VocabularyFactory(id=vocab_id)
        tag_schema = catalog.get_schema(URI(f'https://odp.saeon.ac.za/schema/tag/collection/{vocab_key}'), session=session)
        tag_json = JSON({
            vocab_key: 'foo'
        })
        assert not (result := tag_schema.evaluate(tag_json)).valid
        error = next(
            err for err in result.output('basic')['errors']
            if err['instanceLocation'] == f'/{vocab_key}'
        )
        assert error['error'] == f"Vocabulary '{vocab_id}' does not contain the term 'foo'"


@pytest.mark.parametrize('vocab_id', ['Project', 'Infrastructure'])
def test_vocabulary_keyword_unknown_vocab(vocab_id):
    with catalog.session() as session:
        vocab_key = vocab_id.lower()
        tag_schema = catalog.get_schema(URI(f'https://odp.saeon.ac.za/schema/tag/collection/{vocab_key}'), session=session)
        tag_json = JSON({
            vocab_key: 'foo'
        })
        with pytest.raises(JSONSchemaError) as excinfo:
            tag_schema.evaluate(tag_json)
        assert str(excinfo.value) == f'Unknown vocabulary {vocab_id!r}'
