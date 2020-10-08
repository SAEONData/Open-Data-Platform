from typing import List, Optional

from odp.api.models import Pagination
from odp.api.models.catalogue import CatalogueRecord
from odp.db import session as db_session
from odp.db.models import MetadataStatus


def list_catalogue_records(pagination: Pagination) -> List[CatalogueRecord]:
    return [
        CatalogueRecord(**mdstatus.catalogue_record) if mdstatus.published
        else CatalogueRecord(id=mdstatus.metadata_id, published=False)
        for mdstatus in db_session.query(MetadataStatus).
            order_by(MetadataStatus.created, MetadataStatus.metadata_id).
            limit(pagination.limit).
            offset(pagination.offset).
            all()
    ]


def get_catalogue_record(record_id: str) -> Optional[CatalogueRecord]:
    mdstatus = db_session.query(MetadataStatus).get(record_id)
    if mdstatus and mdstatus.published:
        return CatalogueRecord(**mdstatus.catalogue_record)
