from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class RoleScope(Base):
    """Model of a role-scope many-to-many relationship, representing
    a functional capability of a role."""

    __tablename__ = 'role_scope'

    role_id = Column(Integer, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    scope_id = Column(Integer, ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True)

    role = relationship('Role', back_populates='role_scopes')
    scope = relationship('Scope', back_populates='scope_roles')
