from sqlalchemy import Column, ForeignKey, String, Enum, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import RoleType


class RoleScope(Base):
    """Model of a many-to-many role-scope association."""

    __tablename__ = 'role_scope'

    __table_args__ = (
        ForeignKeyConstraint(
            ('role_id', 'role_type'),
            ('role.id', 'role.type'),
            name='role_scope_role_fkey',
            ondelete='CASCADE',
        ),
    )

    role_id = Column(String, primary_key=True)
    role_type = Column(Enum(RoleType), primary_key=True)
    scope_id = Column(String, ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True)

    role = relationship('Role', back_populates='role_scopes')
    scope = relationship('Scope', back_populates='scope_roles')
