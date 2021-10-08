from sqlalchemy import Column, String, ForeignKey, ForeignKeyConstraint, Enum, CheckConstraint
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import RoleType


class ClientUser(Base):
    """A client role-user assignment."""

    __tablename__ = 'client_user'

    __table_args__ = (
        ForeignKeyConstraint(
            ('role_id', 'role_type'), ('role.id', 'role.type'),
            name='client_user_role_fkey', ondelete='CASCADE',
        ),
        CheckConstraint(
            f"role_type = '{RoleType.CLIENT}'",
            name='client_user_role_type_check',
        ),
    )

    client_id = Column(String, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String, primary_key=True)
    role_type = Column(Enum(RoleType), primary_key=True)

    client = relationship('Client')
    user = relationship('User')
    role = relationship('Role')
