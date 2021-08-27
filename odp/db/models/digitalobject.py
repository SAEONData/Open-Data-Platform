import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base


class DigitalObject(Base):
    """A digital object record."""

    __tablename__ = 'digitalobject'

    __table_args__ = (CheckConstraint('doi IS NOT NULL OR sid IS NOT NULL'),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doi = Column(String, unique=True)
    sid = Column(String, unique=True)
    metadata_ = Column(JSONB, nullable=False)
    validity = Column(JSONB)

    collection_id = Column(Integer, ForeignKey('collection.id', ondelete='RESTRICT'), nullable=False)
    collection = relationship('Collection', back_populates='digitalobjects')

    metadata_schema_id = Column(Integer, ForeignKey('metadata_schema.id', ondelete='RESTRICT'), nullable=False)
    metadata_schema = relationship('MetadataSchema')

    # one-to-many relationship with digitalobject_tag
    tags = relationship('DigitalObjectTag', back_populates='digitalobject', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return self._repr('id', 'doi', 'sid', 'collection', 'metadata_schema')
