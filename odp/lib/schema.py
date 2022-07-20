import hashlib
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from jschon import LocalSource, URI, create_catalog
from jschon.translation import translation_filter

schema_catalog = create_catalog('2020-12', 'translation')
schema_catalog.add_uri_source(
    URI('https://odp.saeon.ac.za/schema/'),
    LocalSource(Path(__file__).parent.parent.parent / 'schema', suffix='.json'),
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
