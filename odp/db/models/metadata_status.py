from sqlalchemy import Column, String, JSON, Boolean, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declared_attr

from odp.db import Base


class MetadataStatus(Base):
    __tablename__ = 'metadata_status'

    metadata_id = Column(String, primary_key=True)
    catalogue_record = Column(JSON, nullable=False)
    published = Column(Boolean, nullable=False)
    updated = Column(TIMESTAMP(timezone=True), nullable=False)
    checked = Column(TIMESTAMP(timezone=True), nullable=False)


class CatalogueStatusMixin:
    @declared_attr
    def metadata_id(cls):
        return Column(String, ForeignKey('metadata_status.metadata_id', ondelete='RESTRICT'), primary_key=True)

    published = Column(Boolean, nullable=False)
    updated = Column(TIMESTAMP(timezone=True))
    checked = Column(TIMESTAMP(timezone=True), nullable=False)
    error = Column(String)
    retries = Column(Integer)
