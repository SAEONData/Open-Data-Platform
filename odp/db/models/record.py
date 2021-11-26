import uuid

from sqlalchemy import Column, String, ForeignKey, CheckConstraint, Enum, ForeignKeyConstraint, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import SchemaType, AuditCommand


class Record(Base):
    """An ODP record.

    This model represents a uniquely identifiable digital object
    and its associated metdata.
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

    collection_id = Column(String, ForeignKey('collection.id', ondelete='RESTRICT'), nullable=False)
    collection = relationship('Collection')

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    # view of associated flags (one-to-many)
    flags = relationship('RecordFlag', viewonly=True)

    # view of associated tags (one-to-many)
    tags = relationship('RecordTag', viewonly=True)

    def __repr__(self):
        return self._repr('id', 'doi', 'sid', 'collection_id', 'schema_id')


class RecordAudit(Base):
    """Record audit log."""
    
    __tablename__ = 'record_audit'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _id = Column(String, nullable=False)
    _doi = Column(String)
    _sid = Column(String)
    _metadata = Column(JSONB)
    _collection_id = Column(String)
    _schema_id = Column(String)
