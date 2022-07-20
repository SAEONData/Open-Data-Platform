from jschon import JSON, URI

from odp import ODPMetadataSchema
from odp.api.models import PublishedMetadataModel, RecordModel
from odp.db import Session
from odp.db.models import Schema, SchemaType
from odp.job.publish import Publisher
from odp.lib.schema import schema_catalog


class SAEONPublisher(Publisher):

    def _create_published_metadata(self, record_model: RecordModel) -> list[PublishedMetadataModel]:
        """Create the published metadata outputs for a record.

        Add DataCite translation to the inherited output, for ISO19115 records.
        """
        published_metadata = super()._create_published_metadata(record_model)

        if record_model.schema_id == ODPMetadataSchema.SAEON_ISO19115:
            schema = Session.get(Schema, (record_model.schema_id, SchemaType.metadata))
            iso19115_schema = schema_catalog.get_schema(URI(schema.uri))
            result = iso19115_schema.evaluate(JSON(record_model.metadata))
            datacite_metadata = result.output('translation', scheme='saeon/datacite-4', ignore_validity=True)
            published_metadata += [
                PublishedMetadataModel(
                    schema_id=ODPMetadataSchema.SAEON_DATACITE_4,
                    metadata=datacite_metadata,
                )
            ]

        return published_metadata
