from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, ForeignKeyConstraint, String
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import ScopeType


class RoleScope(Base):
    """Model of a many-to-many role-scope association."""

    __tablename__ = 'role_scope'

    __table_args__ = (
        ForeignKeyConstraint(
            ('scope_id', 'scope_type'), ('scope.id', 'scope.type'),
            name='role_scope_scope_fkey', ondelete='CASCADE',
        ),
        CheckConstraint(
            f"scope_type in ('{ScopeType.odp}', '{ScopeType.client}')",
            name='role_scope_scope_type_check',
        ),
    )

    role_id = Column(String, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    scope_id = Column(String, primary_key=True)
    scope_type = Column(Enum(ScopeType), primary_key=True)

    role = relationship('Role', viewonly=True)
    scope = relationship('Scope')
