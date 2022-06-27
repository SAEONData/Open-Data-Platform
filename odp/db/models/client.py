from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_scope import ClientScope


class Client(Base):
    """A client application, linked by id with an OAuth2 client
    configuration on Hydra.

    The associated scopes represent the set of permissions granted
    to the client.

    If a client is linked to a collection, then its scopes apply
    only to entities that are associated with that collection.
    """

    __tablename__ = 'client'

    id = Column(String, primary_key=True)

    collection_id = Column(String, ForeignKey('collection.id', onupdate='CASCADE', ondelete='CASCADE'))
    collection = relationship('Collection')

    # many-to-many client_scope entities are persisted by
    # assigning/removing Scope instances to/from scopes
    client_scopes = relationship('ClientScope', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('client_scopes', 'scope', creator=lambda s: ClientScope(scope=s))

    _repr_ = 'id', 'collection_id'
