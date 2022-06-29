from sqlalchemy import Boolean, CheckConstraint, Column, Enum, ForeignKeyConstraint, String
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import SchemaType, ScopeType, TagCardinality, TagType


class Tag(Base):
    """A tag definition."""

    __tablename__ = 'tag'

    __table_args__ = (
        ForeignKeyConstraint(
            ('schema_id', 'schema_type'), ('schema.id', 'schema.type'),
            name='tag_schema_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"schema_type = '{SchemaType.tag}'",
            name='tag_schema_type_check',
        ),
        ForeignKeyConstraint(
            ('scope_id', 'scope_type'), ('scope.id', 'scope.type'),
            name='tag_scope_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"scope_type = '{ScopeType.odp}'",
            name='tag_scope_type_check',
        ),
    )

    id = Column(String, unique=True, primary_key=True)
    type = Column(Enum(TagType), primary_key=True)
    cardinality = Column(Enum(TagCardinality), nullable=False)
    public = Column(Boolean, nullable=False)

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    scope_id = Column(String, nullable=False)
    scope_type = Column(Enum(ScopeType), nullable=False)
    scope = relationship('Scope')

    _repr_ = 'id', 'type', 'cardinality', 'public', 'schema_id', 'scope_id'
