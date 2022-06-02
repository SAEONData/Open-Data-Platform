#!/usr/bin/env python

import logging
from datetime import datetime

from jschon import JSON, URI
from sqlalchemy import func, or_, select

from odp.api.models import CatalogRecordModel, CatalogTagInstanceModel, RecordModel
from odp.api.routers.record import output_record_model
from odp.db import Session
from odp.db.models import Catalog, CatalogRecord, CollectionTag, Record, RecordTag
from odp.lib.schema import schema_catalog

logger = logging.getLogger(__name__)


def run():
    for catalog_id in Session.execute(select(Catalog.id)).scalars():
        for record_id, timestamp in _select_records(catalog_id):
            _evaluate_record(catalog_id, record_id, timestamp)


def _select_records(catalog_id: str) -> list[tuple[str, datetime]]:
    """Select records to be evaluated for publication to, or
    retraction from, a catalog.

    A record is selected if:

    * there is no corresponding catalog_record entry; or
    * catalog_record.timestamp is less than any of the following:

      * catalog.schema.timestamp
      * record.timestamp
      * record_tag.timestamp, for any associated record tag
      * collection_tag.timestamp, for any associated collection tag

    :return: a list of (record_id, timestamp) tuples, where
        timestamp is that of the latest contributing change
    """
    catalog = Session.get(Catalog, catalog_id)

    records_subq = (
        select(
            Record.id.label('record_id'),
            func.greatest(
                catalog.schema.timestamp,
                Record.timestamp,
                func.max(RecordTag.timestamp),
                func.max(CollectionTag.timestamp)
            ).label('max_timestamp')
        ).
        outerjoin(RecordTag).
        outerjoin(CollectionTag, Record.collection_id == CollectionTag.collection_id).
        group_by(Record.id, Record.timestamp).
        subquery()
    )

    catalog_records_subq = (
        select(
            CatalogRecord.record_id,
            CatalogRecord.timestamp
        ).
        where(CatalogRecord.catalog_id == catalog_id).
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
            catalog_records_subq.c.timestamp < records_subq.c.max_timestamp
        ))
    )

    return Session.execute(stmt).all()


def _evaluate_record(catalog_id: str, record_id: str, timestamp: datetime) -> None:
    """Evaluate a record model (API) against the publication schema for
    a catalog, and commit the result to the catalog_record table.

    The catalog_record entry is stamped with the `timestamp` of the latest
    contributing change (from catalog/record/record_tag/collection_tag).
    """
    catalog = Session.get(Catalog, catalog_id)
    record = Session.get(Record, record_id)
    catalog_record = (Session.get(CatalogRecord, (catalog_id, record_id)) or
                      CatalogRecord(catalog_id=catalog_id, record_id=record_id))

    record_model = output_record_model(record)
    record_json = JSON(record_model.dict())

    publication_schema = schema_catalog.get_schema(URI(catalog.schema.uri))

    if (result := publication_schema.evaluate(record_json)).valid:
        catalog_record.published = True
        catalog_record.validity = result.output('flag')
        catalog_record.catalog_record = _create_catalog_record(record_model).dict()
    else:
        catalog_record.published = False
        catalog_record.validity = result.output('detailed')
        catalog_record.catalog_record = None

    catalog_record.timestamp = timestamp
    catalog_record.save()
    Session.commit()


def _create_catalog_record(record_model: RecordModel) -> CatalogRecordModel:
    return CatalogRecordModel(
        id=record_model.id,
        doi=record_model.doi,
        sid=record_model.sid,
        provider_id=record_model.provider_id,
        collection_id=record_model.collection_id,
        project_ids=record_model.project_ids,
        schema_id=record_model.schema_id,
        metadata=record_model.metadata,
        timestamp=record_model.timestamp,
        tags=[CatalogTagInstanceModel(
            tag_id=tag_instance.tag_id,
            data=tag_instance.data,
            user_name=tag_instance.user_name,
            timestamp=tag_instance.timestamp,
            flag=tag_instance.flag,
        ) for tag_instance in record_model.tags if tag_instance.public],
    )


if __name__ == '__main__':
    logger.info('----- publishing started -----')
    run()
    logger.info('----- publishing finished -----')
