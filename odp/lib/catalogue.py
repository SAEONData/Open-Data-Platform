from typing import List, Optional

from odp.api.models import Pagination
from odp.api.models.catalogue import CatalogueRecord
from odp.db.models import CatalogueRecord as CatalogueRecordORM


def list_catalogue_records(pagination: Pagination) -> List[CatalogueRecord]:
    return [
        CatalogueRecord(**catrec.catalogue_record) if catrec.published
        else CatalogueRecord(id=catrec.metadata_id, published=False)
        for catrec in CatalogueRecordORM.query.
            order_by(CatalogueRecordORM.created, CatalogueRecordORM.metadata_id).
            limit(pagination.limit).
            offset(pagination.offset).
            all()
    ]


def get_catalogue_record(record_id: str) -> Optional[CatalogueRecord]:
    catrec = CatalogueRecordORM.query.get(record_id)
    if catrec and catrec.published:
        return CatalogueRecord(**catrec.catalogue_record)


def select_catalogue_records(ids: List[str], pagination: Pagination) -> List[CatalogueRecord]:
    return [
        CatalogueRecord(**catrec.catalogue_record)
        for catrec in CatalogueRecordORM.query.
            filter(CatalogueRecordORM.metadata_id.in_(ids)).
            filter(CatalogueRecordORM.published == True).
            order_by(CatalogueRecordORM.created, CatalogueRecordORM.metadata_id).
            limit(pagination.limit).
            offset(pagination.offset).
            all()
    ]
