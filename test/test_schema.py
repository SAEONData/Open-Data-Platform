import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pytest
from jschon import Catalog, JSON, JSONPatch, LocalSource, URI, create_catalog
from jschon.translation import translation_filter


@translation_filter('date-to-year')
def date_to_year(date: str) -> int:
    return datetime.strptime(date, '%Y-%m-%d').year


@translation_filter('base-url')
def base_url(url: str) -> str:
    u = urlparse(url)
    return f'{u.scheme}://{u.netloc}'


@translation_filter('split-archived-formats')
def split_archived_formats(value: str) -> list:
    """Filter for translating /onlineResources/n/applicationProfile (datacite4-saeon)
    to /immutableResource/resourceDownload/archivedFormats (iso19115-saeon).

    e.g. given "[shp, shx, dbf]", return ["shp", "shx", "dbf"]
    """
    if not re.match("^\\[\\s*\\w+\\s*(,\\s*\\w+\\s*)*]$", value):
        raise ValueError('Invalid input for split-archived-formats filter')
    return [item.strip() for item in value[1:-1].split(',')]


@pytest.fixture(scope='module')
def catalog() -> Catalog:
    cat = create_catalog('2020-12', 'translation')
    cat.add_uri_source(
        URI('https://odp.saeon.ac.za/schema/'),
        LocalSource(Path(__file__).parent.parent / 'schema', suffix='.json'),
    )
    return cat


def test_validity(catalog):
    input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon'))
    input_json = JSON(catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon-example')))
    output_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/datacite4-saeon'))
    output_json = JSON(catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/datacite4-saeon-example-translated')))

    assert input_schema.validate().valid
    assert input_schema.evaluate(input_json).valid
    assert output_schema.validate().valid
    assert output_schema.evaluate(output_json).valid


def test_translate_iso19115_to_datacite(catalog):
    input_schema = catalog.get_schema(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon'))
    input_json = JSON(catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/iso19115-saeon-example.json')))
    output_json = JSON(catalog.load_json(URI('https://odp.saeon.ac.za/schema/metadata/datacite4-saeon-example-translated.json')))

    result = input_schema.evaluate(input_json)
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
