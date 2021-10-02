from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.role_scope import RoleScope
from odp.db.models.user_role import UserRole


class Role(Base):
    """A role is a configuration object that grants a user
    permissions to access ODP entities. If multiple roles are
    assigned to a user, the effective set of permissions is
    taken to be the union of those conferred by the individual
    assigned roles.

    The linked scopes determine what types of operations a user
    may perform on what classes of entity. The applicability of
    those scopes may be constrained by pinning a role to a project
    and/or provider, in which case the scopes grant access only
    to resources linked with the specified project and/or provider.

    A client-specific role confers scope access only for configuring
    or logging in to that client, and would typically be defined to
    permit developer or admin access to a particular application.
    """

    __tablename__ = 'role'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    project_id = Column(String, ForeignKey('project.id', ondelete='CASCADE'))
    project = relationship('Project', back_populates='roles')

    provider_id = Column(String, ForeignKey('provider.id', ondelete='CASCADE'))
    provider = relationship('Provider', back_populates='roles')

    client_id = Column(String, ForeignKey('client.id', ondelete='CASCADE'))
    client = relationship('Client', back_populates='roles')

    # many-to-many relationship between role and user
    role_users = relationship('UserRole', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    users = association_proxy('role_users', 'user', creator=lambda u: UserRole(user=u))

    # many-to-many relationship between role and scope
    role_scopes = relationship('RoleScope', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('role_scopes', 'scope', creator=lambda s: RoleScope(scope=s))

    def __repr__(self):
        return self._repr('id', 'name', 'project', 'provider', 'client')
