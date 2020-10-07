from sqlalchemy import Column, String, JSON, Boolean, TIMESTAMP

from odp.db import Base


class MetadataStatus(Base):
    """Model representing the ODP metadata catalogue."""

    __tablename__ = 'metadata_status'

    metadata_id = Column(String, primary_key=True)
    catalogue_record = Column(JSON, nullable=False)
    published = Column(Boolean, nullable=False)
    updated = Column(TIMESTAMP(timezone=True), nullable=False)
    checked = Column(TIMESTAMP(timezone=True), nullable=False)
