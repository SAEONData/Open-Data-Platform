from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, CheckConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import SchemaType


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
    )

    id = Column(String, primary_key=True)
    public = Column(Boolean, nullable=False)

    scope_id = Column(String, ForeignKey('scope.id', ondelete='RESTRICT'), nullable=False)
    scope = relationship('Scope')

    schema_id = Column(String, nullable=False)
    schema_type = Column(Enum(SchemaType), nullable=False)
    schema = relationship('Schema')

    def __repr__(self):
        return self._repr('id', 'public', 'scope_id', 'schema_id')
