from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from odp.db import Base


class DataciteRecord(Base):
    """Model of a metadata record as published to DataCite."""

    __tablename__ = 'datacite_record'

    metadata_id = Column(String, ForeignKey('catalogue_record.metadata_id', ondelete='RESTRICT'), primary_key=True)
    doi = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True)
    metadata_ = Column(JSONB)
    published = Column(Boolean, nullable=False)
    updated = Column(TIMESTAMP(timezone=True))
    checked = Column(TIMESTAMP(timezone=True), nullable=False)
    error = Column(String)
    retries = Column(Integer)
