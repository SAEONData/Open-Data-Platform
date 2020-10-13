from sqlalchemy import Column, Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from odp.db import Base


class ClientCapability(Base):
    """
    Model of a client-capability many-to-many relationship (client-scope-role),
    representing a capability supported by a client application.
    """
    __tablename__ = 'client_capability'

    client_id = Column(Integer, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)
    scope_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)

    client = relationship('Client', back_populates='client_capabilities')
    capability = relationship('Capability', back_populates='client_capabilities')

    __table_args__ = (
        ForeignKeyConstraint(
            ('scope_id', 'role_id'),
            ('capability.scope_id', 'capability.role_id'),
            name='client_capability_capability_fkey',
            ondelete='CASCADE',
        ),
    )

    scope = relationship('Scope', viewonly=True, foreign_keys=scope_id,
                         primaryjoin='ClientCapability.scope_id == Scope.id')
    role = relationship('Role', viewonly=True, foreign_keys=role_id,
                        primaryjoin='ClientCapability.role_id == Role.id')
