import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base


class DigitalObject(Base):
    """A digital object record."""

    __tablename__ = 'digitalobject'

    __table_args__ = (CheckConstraint('doi IS NOT NULL OR sid IS NOT NULL'))

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doi = Column(String, unique=True)
    sid = Column(String, unique=True)
    metadata = Column(JSONB, nullable=False)
    validity = Column(JSONB)

    collection_id = Column(Integer, ForeignKey('collection.id', ondelete='RESTRICT'), nullable=False)
    collection = relationship('Collection', back_populates='digitalobjects')

    digitalobject_schema_id = Column(Integer, ForeignKey('digitalobject_schema.id', ondelete='RESTRICT'), nullable=False)
    digitalobject_schema = relationship('DigitalObjectSchema')

    def __repr__(self):
        return self._repr('id', 'doi', 'sid', 'collection', 'digitalobject_schema')
