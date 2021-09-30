from sqlalchemy import Column, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_scope import ClientScope
from odp.db.models.role_scope import RoleScope


class Scope(Base):
    """An OAuth2 scope."""

    __tablename__ = 'scope'

    id = Column(String, primary_key=True)

    # many-to-many relationship between scope and role
    scope_roles = relationship('RoleScope', back_populates='scope', cascade='all, delete-orphan', passive_deletes=True)
    roles = association_proxy('scope_roles', 'role', creator=lambda r: RoleScope(role=r))

    # many-to-many relationship between scope and client
    scope_clients = relationship('ClientScope', back_populates='scope', cascade='all, delete-orphan', passive_deletes=True)
    clients = association_proxy('scope_clients', 'client', creator=lambda c: ClientScope(client=c))

    def __repr__(self):
        return self._repr('id')
