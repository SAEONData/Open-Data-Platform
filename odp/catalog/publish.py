from datetime import datetime

from jschon import JSON, URI

from odp.api.routers.record import output_record_model
from odp.db import Session
from odp.db.models import CatalogRecord
from odp.lib.schema import schema_catalog


def select_records(catalog_id: str) -> list[str]:
    """Select records to be evaluated for publication to, or
    retraction from, a catalog.

    A record is selected if:

    * there is no corresponding catalog_record entry; or
    * catalog_record.timestamp is less than any of the following:

      * catalog.timestamp
      * record.timestamp
      * record_tag.timestamp, for any associated record tag
      * collection_tag.timestamp, for any associated collection tag
    """


def evaluate_record(catalog_id: str, record_id: str, timestamp: datetime) -> None:
    """Evaluate a record model (API) against the publication schema for
    a catalog, and commit the result to the catalog_record table.

    The catalog_record entry is stamped with the `timestamp` of the latest
    contributing change (from catalog/record/record_tag/collection_tag).
    """
    catalog_record = (Session.get(CatalogRecord, (catalog_id, record_id)) or
                      CatalogRecord(catalog_id, record_id))

    publication_schema = schema_catalog.get_schema(URI(catalog_record.catalog.schema.uri))
    record_model = output_record_model(catalog_record.record)
    record_dict = record_model.dict()

    if (result := publication_schema.evaluate(JSON(record_dict))).valid:
        catalog_record.validity = result.output('flag')
        catalog_record.catalog_record = record_dict
    else:
        catalog_record.validity = result.output('detailed')
        catalog_record.catalog_record = None

    catalog_record.timestamp = timestamp
    catalog_record.save()
