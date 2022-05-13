from sqlalchemy import Column, Enum, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import ScopeType


class Scope(Base):
    """An OAuth2 scope."""

    __tablename__ = 'scope'

    id = Column(String, primary_key=True, unique=True)
    type = Column(Enum(ScopeType), primary_key=True)

    # view of associated roles via many-to-many role_scope relation
    scope_roles = relationship('RoleScope', viewonly=True)
    roles = association_proxy('scope_roles', 'role')

    # view of associated clients via many-to-many client_scope relation
    scope_clients = relationship('ClientScope', viewonly=True)
    clients = association_proxy('scope_clients', 'client')

    _repr_ = 'id', 'type'
