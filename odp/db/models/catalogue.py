from sqlalchemy import Column, String, Enum, CheckConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import SchemaType


class Catalogue(Base):
    """Represents a public catalogue providing access to published
    digital object records."""

    __tablename__ = 'catalogue'

    __table_args__ = (
        ForeignKeyConstraint(
            ('schema_id', 'schema_type'), ('schema.id', 'schema.type'),
            name='catalogue_schema_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"schema_type = '{SchemaType.catalogue}'",
            name='catalogue_schema_type_check',
        ),
    )

    id = Column(String, primary_key=True)

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    def __repr__(self):
        return self._repr('id', 'schema_id', 'schema_type')
