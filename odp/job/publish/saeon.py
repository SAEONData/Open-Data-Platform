from datetime import datetime

from jschon import JSON, URI

from odp import ODPMetadataSchema
from odp.api.models import PublishedMetadataModel, PublishedRecordModel, PublishedSAEONRecordModel, PublishedTagInstanceModel, RecordModel
from odp.db import Session
from odp.db.models import Schema, SchemaType
from odp.job.publish import Publisher
from odp.lib.schema import schema_catalog


class SAEONPublisher(Publisher):
    def __init__(self, catalog_id: str) -> None:
        super().__init__(catalog_id)
        self.indexed = True

    def create_published_record(self, record_model: RecordModel) -> PublishedRecordModel:
        """Create the published form of a record."""
        return PublishedSAEONRecordModel(
            id=record_model.id,
            doi=record_model.doi,
            sid=record_model.sid,
            collection_id=record_model.collection_id,
            metadata=self._create_published_metadata(record_model),
            tags=self._create_published_tags(record_model),
            timestamp=record_model.timestamp,
        )

    @staticmethod
    def _create_published_metadata(record_model: RecordModel) -> list[PublishedMetadataModel]:
        """Create the published metadata outputs for a record."""
        published_metadata = [
            PublishedMetadataModel(
                schema_id=record_model.schema_id,
                metadata=record_model.metadata,
            )
        ]

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

    @staticmethod
    def _create_published_tags(record_model: RecordModel) -> list[PublishedTagInstanceModel]:
        """Create the published tags for a record."""
        return [
            PublishedTagInstanceModel(
                tag_id=tag_instance.tag_id,
                data=tag_instance.data,
                user_name=tag_instance.user_name,
                timestamp=tag_instance.timestamp,
            ) for tag_instance in record_model.tags if tag_instance.public
        ]

    def create_full_text_index_data(self, published_record: PublishedRecordModel) -> str:
        """Create a string from metadata field values to be indexed for full text search."""
        pass

    def create_keyword_index_data(self, published_record: PublishedRecordModel) -> list[str]:
        """Create an array of metadata keywords to be indexed for keyword search."""
        pass

    def create_spatial_index_data(self, published_record: PublishedRecordModel) -> tuple[float, float, float, float]:
        """Create a NESW tuple of spatial extents to be indexed for spatial search."""
        pass

    def create_temporal_index_data(self, published_record: PublishedRecordModel) -> tuple[datetime, datetime]:
        """Create a start-end tuple of the temporal extent to be indexed for temporal search."""
        pass
