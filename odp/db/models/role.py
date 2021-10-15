from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.role_scope import RoleScope
from odp.db.models.user_role import UserRole


class Role(Base):
    """A role is a configuration object that defines a set of
    permissions - represented by the associated scopes - that
    may be granted to a user.

    If a role is linked to a provider, then any 'provider',
    'collection' and 'record' scopes apply only to those
    entities that are associated with that provider.
    """

    __tablename__ = 'role'

    id = Column(String, primary_key=True)

    provider_id = Column(String, ForeignKey('provider.id', ondelete='CASCADE'))
    provider = relationship('Provider')

    # many-to-many relationship between role and scope
    role_scopes = relationship('RoleScope', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('role_scopes', 'scope', creator=lambda s: RoleScope(scope=s))

    # many-to-many relationship between role and user
    role_users = relationship('UserRole', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    users = association_proxy('role_users', 'user', creator=lambda u: UserRole(user=u))

    def __repr__(self):
        return self._repr('id', 'provider')
