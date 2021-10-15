from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_scope import ClientScope


class Client(Base):
    """Client application config. The associated scopes
    represent the set of permissions granted to the client.

    If a client is linked to a provider, then any 'provider',
    'collection' and 'record' scopes apply only to those
    entities that are associated with that provider.
    """

    __tablename__ = 'client'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    provider_id = Column(String, ForeignKey('provider.id', ondelete='CASCADE'))
    provider = relationship('Provider')

    # many-to-many relationship between client and scope
    client_scopes = relationship('ClientScope', back_populates='client', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('client_scopes', 'scope', creator=lambda s: ClientScope(scope=s))

    def __repr__(self):
        return self._repr('id', 'name', 'provider')
