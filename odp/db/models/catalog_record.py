from sqlalchemy import Boolean, Column, ForeignKey, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base


class CatalogRecord(Base):
    """Model of a many-to-many catalog-record association,
    representing the state of a record with respect to a
    public catalog."""

    __tablename__ = 'catalog_record'

    catalog_id = Column(String, ForeignKey('catalog.id', ondelete='CASCADE'), primary_key=True)
    record_id = Column(String, ForeignKey('record.id', ondelete='CASCADE'), primary_key=True)

    catalog = relationship('Catalog', viewonly=True)
    record = relationship('Record', viewonly=True)

    published = Column(Boolean, nullable=False)
    validity = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    catalog_record = Column(JSONB)
