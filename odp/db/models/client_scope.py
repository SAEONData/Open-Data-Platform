from sqlalchemy import Column, Enum, ForeignKey, ForeignKeyConstraint, String
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import ScopeType


class ClientScope(Base):
    """Model of a many-to-many client-scope association,
    representing the set of OAuth2 scopes that a client
    may request."""

    __tablename__ = 'client_scope'

    __table_args__ = (
        ForeignKeyConstraint(
            ('scope_id', 'scope_type'), ('scope.id', 'scope.type'),
            name='client_scope_scope_fkey', ondelete='CASCADE',
        ),
    )

    client_id = Column(String, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)
    scope_id = Column(String, primary_key=True)
    scope_type = Column(Enum(ScopeType), primary_key=True)

    client = relationship('Client', viewonly=True)
    scope = relationship('Scope')
