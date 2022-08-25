import hashlib
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from jschon import JSON, JSONSchemaError, LocalSource, URI, create_catalog
from jschon.jsonschema import JSONSchema, Result
from jschon.vocabulary import Keyword
from jschon_translation import catalog as translation_catalog, translation_filter

from odp.db import Session
from odp.db.models import Vocabulary, VocabularyTerm


class VocabularyKeyword(Keyword):
    """``vocabulary`` keyword implementation

    The keyword's value is an ODP vocabulary id.

    Validation passes if the instance is a term in
    the referenced vocabulary.
    """

    key = 'vocabulary'
    instance_types = 'string',

    def evaluate(self, instance: JSON, result: Result) -> None:
        if not Session.get(Vocabulary, vocab_id := self.json.data):
            raise JSONSchemaError(f'Unknown vocabulary {vocab_id!r}')

        if Session.get(VocabularyTerm, (vocab_id, instance.data)):
            result.annotate(vocab_id)
        else:
            result.fail(f'Vocabulary {vocab_id !r} does not contain the term {instance.data!r}')


schema_catalog = create_catalog('2020-12')
translation_catalog.initialize(schema_catalog)

schema_catalog.add_uri_source(
    URI('https://odp.saeon.ac.za/schema/'),
    LocalSource(Path(__file__).parent.parent.parent / 'schema', suffix='.json'),
)
schema_catalog.create_vocabulary(
    URI('https://odp.saeon.ac.za/schema/__meta__'),
    VocabularyKeyword,
)
schema_catalog.create_metaschema(
    URI('https://odp.saeon.ac.za/schema/__meta__/schema'),
    URI("https://json-schema.org/draft/2020-12/vocab/core"),
    URI("https://json-schema.org/draft/2020-12/vocab/applicator"),
    URI("https://json-schema.org/draft/2020-12/vocab/unevaluated"),
    URI("https://json-schema.org/draft/2020-12/vocab/validation"),
    URI("https://json-schema.org/draft/2020-12/vocab/format-annotation"),
    URI("https://json-schema.org/draft/2020-12/vocab/meta-data"),
    URI("https://json-schema.org/draft/2020-12/vocab/content"),
    URI("https://jschon.dev/ext/translation"),
    URI('https://odp.saeon.ac.za/schema/__meta__'),
)


def schema_md5(uri: str) -> str:
    """Return an MD5 hash of the (serialized) schema identified by uri."""
    schema = schema_catalog.get_schema(URI(uri))
    return hashlib.md5(str(schema).encode()).hexdigest()


@translation_filter('date-to-year')
def date_to_year(date: str) -> int:
    return datetime.strptime(date, '%Y-%m-%d').year


@translation_filter('base-url')
def base_url(url: str) -> str:
    u = urlparse(url)
    return f'{u.scheme}://{u.netloc}'


@translation_filter('split-archived-formats')
def split_archived_formats(value: str) -> list:
    """Filter for translating /onlineResources/n/applicationProfile (saeon/iso19115)
    to /immutableResource/resourceDownload/archivedFormats (saeon/datacite-4).

    e.g. given "[shp, shx, dbf]", return ["shp", "shx", "dbf"]
    """
    if not re.match(r'^\[\s*\w+\s*(,\s*\w+\s*)*]$', value):
        raise ValueError('Invalid input for split-archived-formats filter')
    return [item.strip() for item in value[1:-1].split(',')]
