from jschon import JSON, URI

from odp import DOI_PREFIX, ODPMetadataSchema
from odp.api.models import PublishedDataCiteRecordModel, PublishedRecordModel, RecordModel
from odp.config import config
from odp.db import Session
from odp.db.models import CatalogRecord, Schema, SchemaType
from odp.job.publish import NotPublishedReason, PublishedReason, Publisher
from odp.lib.datacite import DataciteClient, DataciteRecordIn
from odp.lib.schema import schema_catalog


class DataCitePublisher(Publisher):
    def __init__(self, catalog_id: str) -> None:
        super().__init__(catalog_id)
        self.external = True
        self.datacite = DataciteClient(
            api_url=config.DATACITE.API_URL,
            username=config.DATACITE.USERNAME,
            password=config.DATACITE.PASSWORD,
            doi_prefix=DOI_PREFIX,
        )
        self.doi_base_url = config.DATACITE.DOI_BASE_URL

    def evaluate_record(self, record_model: RecordModel) -> tuple[bool, list[PublishedReason | NotPublishedReason]]:
        """Evaluate whether a record can be published.

        Only records with DOIs can be published to DataCite.

        :return: tuple(can_publish: bool, reasons: list)
        """
        can_publish, reasons = super().evaluate_record(record_model)

        if not record_model.doi:
            if can_publish:
                return False, [NotPublishedReason.NO_DOI]
            return False, reasons + [NotPublishedReason.NO_DOI]

        return can_publish, reasons

    def create_published_record(self, record_model: RecordModel) -> PublishedRecordModel:
        """Create the published form of a record."""
        if record_model.schema_id == ODPMetadataSchema.SAEON_DATACITE_4:
            datacite_metadata = record_model.metadata

        elif record_model.schema_id == ODPMetadataSchema.SAEON_ISO19115:
            schema = Session.get(Schema, (record_model.schema_id, SchemaType.metadata))
            iso19115_schema = schema_catalog.get_schema(URI(schema.uri))
            result = iso19115_schema.evaluate(JSON(record_model.metadata))
            datacite_metadata = result.output('translation', scheme='saeon/datacite-4', ignore_validity=True)

        else:
            raise NotImplementedError

        return PublishedDataCiteRecordModel(
            doi=record_model.doi,
            url=f'{self.doi_base_url}/{record_model.doi}',
            metadata=datacite_metadata,
        )

    def sync_external_record(self, record_id: str) -> None:
        """Create / update / delete a record on the DataCite platform."""
        catalog_record = Session.get(CatalogRecord, (self.catalog_id, record_id))
        if catalog_record.published:
            self.datacite.publish_doi(DataciteRecordIn(**catalog_record.published_record))
        elif doi := catalog_record.record.doi:
            self.datacite.unpublish_doi(doi)
