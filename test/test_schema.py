from jschon import JSON, JSONPatch, URI

from odp.api.lib.schema import schema_catalog as catalog


def test_validity():
    input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon'))
    input_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon-example'))
    output_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/datacite4-saeon'))
    output_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/datacite4-saeon-example-translated'))

    assert input_schema.validate().valid
    assert input_schema.evaluate(JSON(input_json)).valid
    assert output_schema.validate().valid
    assert output_schema.evaluate(JSON(output_json)).valid


def test_translate_iso19115_to_datacite():
    input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon'))
    input_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon-example.json'))
    output_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/datacite4-saeon-example-translated.json'))

    result = input_schema.evaluate(JSON(input_json))
    patch = result.output('patch', scheme='datacite4-saeon')
    translation = result.output('translation', scheme='datacite4-saeon')

    assert JSONPatch(*patch).evaluate(None) == translation

    # work in progress
    # assert translation == output_json
    assert translation.keys() == output_json.keys()
    for k in translation:
        if k == 'contributors':
            # todo: resolve leftover empty arrays/objects when there are
            #  no source values to fill them
            continue
        assert translation[k] == output_json[k]
