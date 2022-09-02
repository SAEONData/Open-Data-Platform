import logging
from datetime import date, datetime
from enum import Enum
from typing import final

from sqlalchemy import func, or_, select

from odp import ODPCollectionTag, ODPMetadataSchema, ODPRecordTag
from odp.api.models import PublishedRecordModel, RecordModel
from odp.api.routers.record import output_record_model
from odp.db import Session
from odp.db.models import CatalogRecord, Collection, PublishedDOI, Record, RecordTag

logger = logging.getLogger(__name__)


class PublishedReason(str, Enum):
    QC_PASSED = 'QC passed'
    COLLECTION_READY = 'collection ready'
    MIGRATED_PUBLISHED = 'migrated published'


class NotPublishedReason(str, Enum):
    QC_FAILED = 'QC failed'
    COLLECTION_NOT_READY = 'collection not ready'
    METADATA_INVALID = 'metadata invalid'
    RECORD_RETRACTED = 'record retracted'
    MIGRATED_NOT_PUBLISHED = 'migrated not published'
    NO_DOI = 'no DOI'


class Publisher:
    def __init__(self, catalog_id: str) -> None:
        self.catalog_id = catalog_id
        self.external = False
        self.max_attempts = 3

    @final
    def run(self) -> None:
        records = self._select_records()
        logger.info(f'{self.catalog_id} catalog: {(total := len(records))} records selected for evaluation')

        published = 0
        for record_id, timestamp in records:
            published += self._sync_catalog_record(record_id, timestamp)

        if total:
            logger.info(f'{self.catalog_id} catalog: {published} records published; {total - published} records hidden')

        if self.external:
            self._sync_external()

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
    def _sync_catalog_record(self, record_id: str, timestamp: datetime) -> bool:
        """Synchronize a catalog_record entry with the current state of the
        corresponding record.

        The catalog_record entry is stamped with the `timestamp` of the latest
        contributing change (from record / collection).
        """
        catalog_record = (Session.get(CatalogRecord, (self.catalog_id, record_id)) or
                          CatalogRecord(catalog_id=self.catalog_id, record_id=record_id))

        record = Session.get(Record, record_id)
        record_model = output_record_model(record)

        can_publish, reasons = self.evaluate_record(record_model)
        if can_publish:
            self._process_embargoes(record_model)
            self._save_published_doi(record_model)
            catalog_record.published = True
            catalog_record.published_record = self.create_published_record(record_model).dict()
        else:
            catalog_record.published = False
            catalog_record.published_record = None

        if self.external:
            catalog_record.synced = False
            catalog_record.error = None
            catalog_record.error_count = 0

        catalog_record.reason = ' | '.join(reasons)
        catalog_record.timestamp = timestamp
        catalog_record.save()
        Session.commit()

        return catalog_record.published

    def evaluate_record(self, record_model: RecordModel) -> tuple[bool, list[PublishedReason | NotPublishedReason]]:
        """Evaluate whether a record can be published.

        Universal rules are defined here; derived Publisher classes
        may extend these with catalog-specific rules.

        :return: tuple(can_publish: bool, reasons: list)
        """
        # tag for a record migrated without any subsequent changes
        migrated_tag = next(
            (tag for tag in record_model.tags if tag.tag_id == ODPRecordTag.MIGRATED and
             datetime.fromisoformat(tag.timestamp) >= datetime.fromisoformat(record_model.timestamp)),
            None
        )
        collection_ready = any(
            (tag for tag in record_model.tags if tag.tag_id == ODPCollectionTag.READY)
        )
        qc_passed = any(
            (tag for tag in record_model.tags if tag.tag_id == ODPRecordTag.QC and tag.data['pass_'])
        ) and not any(
            (tag for tag in record_model.tags if tag.tag_id == ODPRecordTag.QC and not tag.data['pass_'])
        )
        retracted = any(
            (tag for tag in record_model.tags if tag.tag_id == ODPRecordTag.RETRACTED)
        )
        metadata_valid = record_model.validity['valid']

        published_reasons = []
        not_published_reasons = []

        # collection readiness applies to both migrated and non-migrated records
        if collection_ready:
            published_reasons += [PublishedReason.COLLECTION_READY]
        else:
            not_published_reasons += [NotPublishedReason.COLLECTION_NOT_READY]

        if migrated_tag:
            if migrated_tag.data['published']:
                published_reasons += [PublishedReason.MIGRATED_PUBLISHED]
            else:
                not_published_reasons += [NotPublishedReason.MIGRATED_NOT_PUBLISHED]

        else:
            if qc_passed:
                published_reasons += [PublishedReason.QC_PASSED]
            else:
                not_published_reasons += [NotPublishedReason.QC_FAILED]

            if retracted:
                not_published_reasons += [NotPublishedReason.RECORD_RETRACTED]

            if not metadata_valid:
                not_published_reasons += [NotPublishedReason.METADATA_INVALID]

        if not_published_reasons:
            return False, not_published_reasons

        return True, published_reasons

    def create_published_record(self, record_model: RecordModel) -> PublishedRecordModel:
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

    @final
    def _sync_external(self) -> None:
        """Synchronize with an external catalog."""
        unsynced_catalog_records = Session.execute(
            select(CatalogRecord).
            where(CatalogRecord.catalog_id == self.catalog_id).
            where(CatalogRecord.synced == False).
            where(CatalogRecord.error_count < self.max_attempts)
        ).scalars().all()

        logger.info(f'{self.catalog_id} catalog: {(total := len(unsynced_catalog_records))} records selected for external sync')
        synced = 0

        for catalog_record in unsynced_catalog_records:
            try:
                self.sync_external_record(catalog_record.record_id)
                catalog_record.synced = True
                catalog_record.error = None
                catalog_record.error_count = 0
                synced += 1
            except Exception as e:
                catalog_record.error = repr(e)
                catalog_record.error_count += 1

            catalog_record.save()
            Session.commit()

        if total:
            logger.info(f'{self.catalog_id} catalog: {synced} records synced; {total - synced} errors')

    def sync_external_record(self, record_id: str) -> None:
        """Create / update / delete a record on an external catalog."""
        pass
