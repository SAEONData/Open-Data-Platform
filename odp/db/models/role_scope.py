from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from odp.db import Base


class RoleScope(Base):
    """Model of a many-to-many role-scope association."""

    __tablename__ = 'role_scope'

    role_id = Column(String, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    scope_id = Column(String, ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True)

    role = relationship('Role', back_populates='role_scopes')
    scope = relationship('Scope', back_populates='scope_roles')
