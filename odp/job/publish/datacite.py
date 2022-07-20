from jschon import JSON, URI
from pydantic import BaseModel

from odp import ODPMetadataSchema
from odp.api.models import RecordModel
from odp.db import Session
from odp.db.models import Schema, SchemaType
from odp.job.publish import Publisher
from odp.lib.schema import schema_catalog


class DataCitePublisher(Publisher):

    def can_publish_record(self, record_model: RecordModel) -> bool:
        """Determine whether or not a record can be published.

        Only records with DOIs can be published to DataCite.
        """
        return (
                record_model.doi and
                super().can_publish_record(record_model)
        )

    def create_published_record(self, record_model: RecordModel) -> BaseModel:
        """Create the published form of a record."""
        if record_model.schema_id == ODPMetadataSchema.SAEON_DATACITE_4:
            datacite_metadata = record_model.metadata

        elif record_model.schema_id == ODPMetadataSchema.SAEON_ISO19115:
            schema = Session.get(Schema, (record_model.schema_id, SchemaType.metadata))
            iso19115_schema = schema_catalog.get_schema(URI(schema.uri))
            result = iso19115_schema.evaluate(JSON(record_model.metadata))
            datacite_metadata = result.output('translation', scheme='saeon/datacite-4', ignore_validity=True)
