from sqlalchemy import Column, String, ForeignKey, ForeignKeyConstraint, Enum
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import RoleType


class UserRole(Base):
    """Model of a many-to-many user-role association."""

    __tablename__ = 'user_role'

    __table_args__ = (
        ForeignKeyConstraint(
            ('role_id', 'role_type'),
            ('role.id', 'role.type'),
            name='user_role_role_fkey',
            ondelete='CASCADE',
        ),
    )

    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String, primary_key=True)
    role_type = Column(Enum(RoleType), primary_key=True)

    user = relationship('User', back_populates='user_roles')
    role = relationship('Role', back_populates='role_users')
