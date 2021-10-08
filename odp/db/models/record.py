import uuid

from sqlalchemy import Column, String, ForeignKey, CheckConstraint, Enum, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import SchemaType


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
    validity = Column(JSONB)

    collection_id = Column(String, ForeignKey('collection.id', ondelete='RESTRICT'), nullable=False)
    collection = relationship('Collection')

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    # one-to-many relationship with record_tag
    tags = relationship('RecordTag', back_populates='record', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return self._repr('id', 'doi', 'sid', 'collection', 'schema')
