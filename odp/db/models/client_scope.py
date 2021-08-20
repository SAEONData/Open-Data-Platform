from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class ClientScope(Base):
    """Model of a client-scope many-to-many relationship, representing
    a functional capability of an application."""

    __tablename__ = 'client_scope'

    client_id = Column(String, ForeignKey('client.id', ondelete='CASCADE'), primary_key=True)
    scope_id = Column(Integer, ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True)

    client = relationship('Client', back_populates='client_scopes')
    scope = relationship('Scope', back_populates='scope_clients')
