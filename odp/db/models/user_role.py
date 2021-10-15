from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class UserRole(Base):
    """A user-role assignment."""

    __tablename__ = 'user_role'

    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)

    user = relationship('User', back_populates='user_roles')
    role = relationship('Role', back_populates='role_users')
