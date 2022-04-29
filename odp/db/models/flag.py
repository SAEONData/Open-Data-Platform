from sqlalchemy import Boolean, CheckConstraint, Column, Enum, ForeignKeyConstraint, String
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import FlagType, SchemaType, ScopeType


class Flag(Base):
    """A flag definition."""

    __tablename__ = 'flag'

    __table_args__ = (
        ForeignKeyConstraint(
            ('schema_id', 'schema_type'), ('schema.id', 'schema.type'),
            name='flag_schema_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"schema_type = '{SchemaType.flag}'",
            name='flag_schema_type_check',
        ),
        ForeignKeyConstraint(
            ('scope_id', 'scope_type'), ('scope.id', 'scope.type'),
            name='flag_scope_fkey', ondelete='RESTRICT',
        ),
        CheckConstraint(
            f"scope_type = '{ScopeType.odp}'",
            name='flag_scope_type_check',
        ),
    )

    id = Column(String, unique=True, primary_key=True)
    type = Column(Enum(FlagType), primary_key=True)
    public = Column(Boolean, nullable=False)

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    scope_id = Column(String, nullable=False)
    scope_type = Column(Enum(ScopeType), nullable=False)
    scope = relationship('Scope')

    def __repr__(self):
        return self._repr('id', 'type', 'public', 'schema_id', 'scope_id')
