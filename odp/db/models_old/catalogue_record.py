from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB

from odp.db import Base


class CatalogueRecord(Base):
    """Model of a metadata record as published to the ODP catalogue."""

    __tablename__ = 'catalogue_record'

    metadata_id = Column(String, primary_key=True)
    catalogue_record = Column(JSONB, nullable=False)  # odp.api.models.catalogue.CatalogueRecord
    published = Column(Boolean, nullable=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated = Column(TIMESTAMP(timezone=True), nullable=False)
    checked = Column(TIMESTAMP(timezone=True), nullable=False)

    # We want to be able to sort on created to provide a stable ordering at the
    # catalogue harvest endpoint. However, given that a series of consecutive
    # records might have identical timestamps, we order by id as well.
    __table_args__ = (Index('ix_catalogue_record_created_metadata_id', 'created', 'metadata_id'),)
