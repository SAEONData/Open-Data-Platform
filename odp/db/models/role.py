from sqlalchemy import Column, String, Enum
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.role_scope import RoleScope
from odp.db.models.types import RoleType


class Role(Base):
    """A role is a configuration object that defines a set of
    permissions, represented by the associated scopes.

    The role type determines whether those scopes may be applied
    platform-wide, or only within the context of a client, project
    or provider.
    """

    __tablename__ = 'role'

    id = Column(String, unique=True, primary_key=True)
    type = Column(Enum(RoleType), primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # many-to-many relationship between role and scope
    role_scopes = relationship('RoleScope', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('role_scopes', 'scope', creator=lambda s: RoleScope(scope=s))

    def __repr__(self):
        return self._repr('id', 'type', 'name')
