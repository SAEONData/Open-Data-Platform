from sqlalchemy import Column, ForeignKey, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base


class CatalogRecord(Base):
    """Model of a many-to-many catalog-record association.

    `validity` is the result of evaluating a record model (API output)
    against the schema for a catalog; if such evaluation passes, the
    record is taken to be published to the catalog.
    """

    __tablename__ = 'catalog_record'

    catalog_id = Column(String, ForeignKey('catalog.id', ondelete='CASCADE'), primary_key=True)
    record_id = Column(String, ForeignKey('record.id', ondelete='CASCADE'), primary_key=True)

    catalog = relationship('Catalog', viewonly=True)
    record = relationship('Record', viewonly=True)

    validity = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    catalog_record = Column(JSONB)
