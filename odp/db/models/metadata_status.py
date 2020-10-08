from sqlalchemy import Column, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from odp.db import Base


class MetadataStatus(Base):
    """Model representing the ODP metadata catalogue."""

    __tablename__ = 'metadata_status'

    metadata_id = Column(String, primary_key=True)
    catalogue_record = Column(JSONB, nullable=False)
    published = Column(Boolean, nullable=False)
    updated = Column(TIMESTAMP(timezone=True), nullable=False)
    checked = Column(TIMESTAMP(timezone=True), nullable=False)
