from typing import Optional

from odp.api.models import PublishedDataCiteRecordModel, PublishedRecordModel, PublishedSAEONRecordModel, TagInstanceModel
from odp.db.models import CatalogRecord, CollectionTag, RecordTag
from odplib.const import ODPCatalog


def output_tag_instance_model(tag_instance: CollectionTag | RecordTag) -> TagInstanceModel:
    return TagInstanceModel(
        id=tag_instance.id,
        tag_id=tag_instance.tag_id,
        user_id=tag_instance.user_id,
        user_name=tag_instance.user.name if tag_instance.user_id else None,
        data=tag_instance.data,
        timestamp=tag_instance.timestamp.isoformat(),
        cardinality=tag_instance.tag.cardinality,
        public=tag_instance.tag.public,
    )


def output_published_record_model(catalog_record: CatalogRecord) -> Optional[PublishedRecordModel]:
    if not catalog_record.published:
        return None

    if catalog_record.catalog_id == ODPCatalog.SAEON:
        return PublishedSAEONRecordModel(**catalog_record.published_record)

    if catalog_record.catalog_id == ODPCatalog.DATACITE:
        return PublishedDataCiteRecordModel(**catalog_record.published_record)
