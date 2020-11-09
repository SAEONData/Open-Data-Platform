from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from odp.db import Base


class DataciteStatus(Base):
    """Model representing the status of metadata on DataCite servers."""

    __tablename__ = 'datacite_status'

    metadata_id = Column(String, ForeignKey('metadata_status.metadata_id', ondelete='RESTRICT'), primary_key=True)
    doi = Column(String, unique=True, nullable=False)
    datacite_record = Column(JSONB)
    published = Column(Boolean, nullable=False)
    updated = Column(TIMESTAMP(timezone=True))
    checked = Column(TIMESTAMP(timezone=True), nullable=False)
    error = Column(String)
    retries = Column(Integer)
