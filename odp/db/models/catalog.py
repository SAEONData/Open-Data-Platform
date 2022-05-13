from sqlalchemy import CheckConstraint, Column, Enum, ForeignKeyConstraint, String
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import SchemaType


class Catalog(Base):
    """Represents a public catalog providing access to published
    digital object records."""

    __tablename__ = 'catalog'

    __table_args__ = (
        ForeignKeyConstraint(
            ('schema_id', 'schema_type'), ('schema.id', 'schema.type'),
            name='catalog_schema_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"schema_type = '{SchemaType.catalog}'",
            name='catalog_schema_type_check',
        ),
    )

    id = Column(String, primary_key=True)

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    _repr_ = 'id', 'schema_id'
