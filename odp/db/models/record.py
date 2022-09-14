import uuid

from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, ForeignKeyConstraint, Identity, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import AuditCommand, SchemaType


class Record(Base):
    """An ODP record.

    This model represents a uniquely identifiable digital object
    and its associated metadata.
    """

    __tablename__ = 'record'

    __table_args__ = (
        ForeignKeyConstraint(
            ('schema_id', 'schema_type'), ('schema.id', 'schema.type'),
            name='record_schema_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"schema_type = '{SchemaType.metadata}'",
            name='record_schema_type_check',
        ),
        CheckConstraint(
            'doi IS NOT NULL OR sid IS NOT NULL',
            name='record_doi_sid_check',
        ),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doi = Column(String, unique=True)
    sid = Column(String, unique=True)
    metadata_ = Column(JSONB, nullable=False)
    validity = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    collection_id = Column(String, ForeignKey('collection.id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    collection = relationship('Collection')

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    # view of associated tags (one-to-many)
    tags = relationship('RecordTag', viewonly=True)

    # view of associated catalog records (one-to-many)
    catalog_records = relationship('CatalogRecord', viewonly=True)

    _repr_ = 'id', 'doi', 'sid', 'collection_id', 'schema_id'


class RecordAudit(Base):
    """Record audit log."""

    __tablename__ = 'record_audit'

    id = Column(Integer, Identity(), primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _id = Column(String, nullable=False)
    _doi = Column(String)
    _sid = Column(String)
    _metadata = Column(JSONB, nullable=False)
    _collection_id = Column(String, nullable=False)
    _schema_id = Column(String, nullable=False)
