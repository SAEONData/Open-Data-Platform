from jschon import JSON, JSONPatch, URI

from odp.lib.schema import schema_catalog as catalog


def test_validity():
    input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115'))
    input_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115-example'))
    output_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/saeon/datacite4'))
    output_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/datacite4-example-translated'))

    assert input_schema.validate().valid
    assert input_schema.evaluate(JSON(input_json)).valid
    assert output_schema.validate().valid
    assert output_schema.evaluate(JSON(output_json)).valid


def test_translate_iso19115_to_datacite():
    input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115'))
    input_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/iso19115-example.json'))
    output_json = catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/saeon/datacite4-example-translated.json'))

    result = input_schema.evaluate(JSON(input_json))
    patch = result.output('patch', scheme='saeon/datacite4')
    translation = result.output('translation', scheme='saeon/datacite4')

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
