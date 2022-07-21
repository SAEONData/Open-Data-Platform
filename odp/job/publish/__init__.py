import logging
from datetime import date, datetime
from typing import final

from pydantic import BaseModel
from sqlalchemy import func, or_, select

from odp import ODPCollectionTag, ODPMetadataSchema, ODPRecordTag
from odp.api.models import RecordModel
from odp.api.routers.record import output_record_model
from odp.db import Session
from odp.db.models import CatalogRecord, Collection, PublishedDOI, Record, RecordTag

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, catalog_id: str) -> None:
        self.catalog_id = catalog_id

    @final
    def run(self) -> None:
        records = self._select_records()
        logger.info(f'{self.catalog_id} catalog: {(total := len(records))} records selected for evaluation')

        published = 0
        for record_id, timestamp in records:
            published += self._evaluate_record(record_id, timestamp)

        if total:
            logger.info(f'{self.catalog_id} catalog: {published} records published; {total - published} records hidden')

    @final
    def _select_records(self) -> list[tuple[str, datetime]]:
        """Select records to be evaluated for publication to, or
        retraction from, a catalog.

        A record is selected if:

        * there is no corresponding catalog_record entry; or
        * the record has any embargo tags; or
        * catalog_record.timestamp is less than any of:

          * collection.timestamp
          * record.timestamp

        :return: a list of (record_id, timestamp) tuples, where
            timestamp is that of the latest contributing change
        """
        records_subq = (
            select(
                Record.id.label('record_id'),
                func.greatest(
                    Collection.timestamp,
                    Record.timestamp,
                ).label('max_timestamp')
            ).
            join(Collection).
            subquery()
        )

        catalog_records_subq = (
            select(
                CatalogRecord.record_id,
                CatalogRecord.timestamp
            ).
            where(CatalogRecord.catalog_id == self.catalog_id).
            subquery()
        )

        stmt = (
            select(
                records_subq.c.record_id,
                records_subq.c.max_timestamp
            ).
            outerjoin_from(records_subq, catalog_records_subq).
            where(or_(
                catalog_records_subq.c.record_id == None,
                catalog_records_subq.c.timestamp < records_subq.c.max_timestamp,
                catalog_records_subq.c.record_id.in_(
                    select(RecordTag.record_id).
                    where(RecordTag.tag_id == ODPRecordTag.EMBARGO)
                )
            ))
        )

        return Session.execute(stmt).all()

    @final
    def _evaluate_record(self, record_id: str, timestamp: datetime) -> bool:
        """Evaluate a record and commit the result to the catalog_record table.

        The catalog_record entry is stamped with the `timestamp` of the latest
        contributing change (from catalog/record/record_tag/collection_tag).
        """
        catalog_record = (Session.get(CatalogRecord, (self.catalog_id, record_id)) or
                          CatalogRecord(catalog_id=self.catalog_id, record_id=record_id))

        record = Session.get(Record, record_id)
        record_model = output_record_model(record)

        if self.can_publish_record(record_model):
            self._process_embargoes(record_model)
            self._save_published_doi(record_model)
            catalog_record.published = True
            catalog_record.published_record = self.create_published_record(record_model).dict()
        else:
            catalog_record.published = False
            catalog_record.published_record = None

        catalog_record.timestamp = timestamp
        catalog_record.save()
        Session.commit()

        return catalog_record.published

    def can_publish_record(self, record_model: RecordModel) -> bool:
        """Determine whether or not a record can be published.

        Universal rules are defined here; derived Publisher classes
        may extend these with catalog-specific rules.
        """
        # if the collection is not tagged as ready, then the record cannot be published
        if not any(
                (tag for tag in record_model.tags
                 if tag.tag_id == ODPCollectionTag.READY)
        ):
            return False

        # if the record was migrated with a status of published, and there have
        # been no subsequent changes to the record, then it can be published
        if any(
                (tag for tag in record_model.tags
                 if tag.tag_id == ODPRecordTag.MIGRATED and tag.data['published'] and
                    datetime.fromisoformat(tag.timestamp) >= datetime.fromisoformat(record_model.timestamp))
        ):
            return True

        # if the record is invalid against the metadata schema, then it cannot be published
        if not record_model.validity['valid']:
            return False

        # if the record has any QC tags with a status of failed, then it cannot be published
        if any(
                (tag for tag in record_model.tags
                 if tag.tag_id == ODPRecordTag.QC and not tag.data['pass_'])
        ):
            return False

        # if the record does not have any QC tags with a status of passed, then it cannot be published
        if not any(
                (tag for tag in record_model.tags
                 if tag.tag_id == ODPRecordTag.QC and tag.data['pass_'])
        ):
            return False

        # all checks have passed; the record can be published
        return True

    def create_published_record(self, record_model: RecordModel) -> BaseModel:
        """Create the published form of a record."""
        raise NotImplementedError

    @staticmethod
    def _process_embargoes(record_model: RecordModel) -> None:
        """Check if a record is currently subject to an embargo and, if so, update
        the given `record_model`, stripping out download links / embedded datasets
        from the metadata."""
        current_date = date.today()
        embargoed = False

        for tag in record_model.tags:
            if tag.tag_id == ODPRecordTag.EMBARGO:
                start_date = date.fromisoformat(tag.data['start'])
                end_date = date.fromisoformat(tag.data['end'] or '3000-01-01')
                if start_date <= current_date <= end_date:
                    embargoed = True
                    break

        if not embargoed:
            return

        if record_model.schema_id == ODPMetadataSchema.SAEON_DATACITE_4:
            try:
                if 'resourceDownload' in record_model.metadata['immutableResource']:
                    record_model.metadata['immutableResource']['resourceDownload']['downloadURL'] = None
            except KeyError:
                pass
            try:
                if 'resourceData' in record_model.metadata['immutableResource']:
                    record_model.metadata['immutableResource']['resourceData'] = None
            except KeyError:
                pass

        elif record_model.schema_id == ODPMetadataSchema.SAEON_ISO19115:
            for item in record_model.metadata.get('onlineResources', []):
                try:
                    if item['description'] == 'download':
                        item['linkage'] = None
                except KeyError:
                    pass

    @staticmethod
    def _save_published_doi(record_model: RecordModel) -> None:
        """Permanently save a DOI when it is first published."""
        if record_model.doi and not Session.get(PublishedDOI, record_model.doi):
            published_doi = PublishedDOI(doi=record_model.doi)
            published_doi.save()
