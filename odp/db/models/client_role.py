from sqlalchemy import Column, String, ForeignKey, ForeignKeyConstraint, Enum, CheckConstraint
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import RoleType


class ClientRole(Base):
    """Model of a many-to-many client-role association."""

    __tablename__ = 'client_role'

    __table_args__ = (
        ForeignKeyConstraint(
            ('role_id', 'role_type'),
            ('role.id', 'role.type'),
            name='client_role_role_fkey',
            ondelete='CASCADE',
        ),
        CheckConstraint(
            f"role_type = '{RoleType.CLIENT}'",
            name='client_role_role_type_check',
        ),
    )

    client_id = Column(String, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String, primary_key=True)
    role_type = Column(Enum(RoleType), primary_key=True)

    client = relationship('Client', back_populates='client_roles')
    role = relationship('Role', back_populates='role_clients')
