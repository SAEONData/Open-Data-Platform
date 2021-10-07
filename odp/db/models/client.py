from sqlalchemy import Column, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_role import ClientRole
from odp.db.models.client_scope import ClientScope


class Client(Base):
    """A client application.

    The many-to-many client-scope relation represents the
    set of OAuth2 scopes that a client may request.
    """

    __tablename__ = 'client'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # many-to-many relationship between client and scope
    client_scopes = relationship('ClientScope', back_populates='client', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('client_scopes', 'scope', creator=lambda s: ClientScope(scope=s))

    # many-to-many relationship between client and role
    client_roles = relationship('ClientRole', back_populates='client', cascade='all, delete-orphan', passive_deletes=True)
    roles = association_proxy('client_roles', 'role', creator=lambda r: ClientRole(role=r))

    def __repr__(self):
        return self._repr('id', 'name')
