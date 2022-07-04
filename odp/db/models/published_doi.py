from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, String, TIMESTAMP

from odp.db import Base


class PublishedDOI(Base):
    """This table preserves all DOIs that have ever been published, and
    prevents associated records from being deleted or having their DOIs
    changed or removed."""

    __tablename__ = 'published_doi'

    doi = Column(String, ForeignKey('record.doi', ondelete='RESTRICT', onupdate='RESTRICT'), primary_key=True)
    published = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
