from odp.api.models import TagInstanceModel
from odp.db.models import CollectionTag, RecordTag


def output_tag_instance_model(tag_instance: CollectionTag | RecordTag) -> TagInstanceModel:
    return TagInstanceModel(
        tag_id=tag_instance.tag_id,
        user_id=tag_instance.user_id,
        user_name=tag_instance.user.name if tag_instance.user_id else None,
        data=tag_instance.data,
        timestamp=tag_instance.timestamp.isoformat(),
        cardinality=tag_instance.tag.cardinality,
        public=tag_instance.tag.public,
    )
