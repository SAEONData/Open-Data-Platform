from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.role_scope import RoleScope


class Role(Base):
    """A role is a configuration object that defines a set of
    permissions - represented by the associated scopes - that
    may be granted to a user.

    If a role is linked to a provider, then its scopes apply
    only to entities that are associated with that provider.
    """

    __tablename__ = 'role'

    id = Column(String, primary_key=True)

    provider_id = Column(String, ForeignKey('provider.id', ondelete='CASCADE'))
    provider = relationship('Provider')

    # many-to-many role_scope entities are persisted by
    # assigning/removing Scope instances to/from scopes
    role_scopes = relationship('RoleScope', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('role_scopes', 'scope', creator=lambda s: RoleScope(scope=s))

    # view of associated users via many-to-many user_role relation
    role_users = relationship('UserRole', viewonly=True)
    users = association_proxy('role_users', 'user')

    _repr_ = 'id', 'provider_id'
