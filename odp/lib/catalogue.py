from typing import List, Optional

from odp.api.models import Pagination
from odp.api.models.catalogue import CatalogueRecord
from odp.db.models import CatalogueRecord as CatalogueRecordORM


def list_catalogue_records(
        institution_key: Optional[str],
        include_unpublished: bool,
        pagination: Pagination,
) -> List[CatalogueRecord]:
    """Return a list of CatalogueRecord (API model) instances
    queried from the catalogue_record table.

    :param institution_key: optional filter on institution key
    :param include_unpublished: True to include un-published records; these
        will have only the `id` and `published` (== `False`) fields set
    :param pagination: standard pagination params
    """
    query = CatalogueRecordORM.query.order_by(
        CatalogueRecordORM.created, CatalogueRecordORM.metadata_id)

    if institution_key:
        query = query.filter(CatalogueRecordORM.catalogue_record.comparator.contains({
            'institution_key': institution_key}))

    if not include_unpublished:
        query = query.filter_by(published=True)

    query = query.limit(pagination.limit).offset(pagination.offset)

    return [
        CatalogueRecord(**catrec.catalogue_record) if catrec.published
        else CatalogueRecord(id=catrec.metadata_id, published=False)
        for catrec in query.all()
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
