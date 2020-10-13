from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_capability import ClientCapability


class Client(Base):
    """
    Model representing a client application.
    """
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)  # the OAuth2 client_id
    institution_id = Column(Integer, ForeignKey('institution.id', ondelete='CASCADE'), nullable=False)

    institution = relationship('Institution', back_populates='clients')

    # many-to-many relationship between client and capability represented by client_capability
    client_capabilities = relationship('ClientCapability',
                                       back_populates='client',
                                       cascade='all, delete-orphan',
                                       passive_deletes=True)
    # enables working with the other side of the relationship transparently
    capabilities = association_proxy('client_capabilities', 'capability',
                                     creator=lambda c: ClientCapability(capability=c))

    def __repr__(self):
        return '<Client %s>' % self.key
