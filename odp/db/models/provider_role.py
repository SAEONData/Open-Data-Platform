from sqlalchemy import Column, String, ForeignKey, ForeignKeyConstraint, Enum, CheckConstraint
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import RoleType


class ProviderRole(Base):
    """Model of a many-to-many provider-role association."""

    __tablename__ = 'provider_role'

    __table_args__ = (
        ForeignKeyConstraint(
            ('role_id', 'role_type'),
            ('role.id', 'role.type'),
            name='provider_role_role_fkey',
            ondelete='CASCADE',
        ),
        CheckConstraint(
            f"role_type = '{RoleType.PROVIDER}'",
            name='provider_role_role_type_check',
        ),
    )

    provider_id = Column(String, ForeignKey('provider.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String, primary_key=True)
    role_type = Column(Enum(RoleType), primary_key=True)

    provider = relationship('Provider', back_populates='provider_roles')
    role = relationship('Role', back_populates='role_providers')
