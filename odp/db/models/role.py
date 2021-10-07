from sqlalchemy import Column, String, Enum
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_role import ClientRole
from odp.db.models.project_role import ProjectRole
from odp.db.models.provider_role import ProviderRole
from odp.db.models.role_scope import RoleScope
from odp.db.models.types import RoleType
from odp.db.models.user_role import UserRole


class Role(Base):
    """A role is a configuration object that grants a user
    permissions to access ODP entities. If multiple roles are
    assigned to a user, the effective set of permissions is
    taken to be the union of those conferred by the individual
    assigned roles.

    The linked scopes determine what types of operations a user
    may perform on what classes of entity. The applicability of
    those scopes may be constrained by pinning a role to a set of
    clients, projects or providers, in which case the scopes grant
    access only to resources linked with the specified clients,
    projects or providers.
    """

    __tablename__ = 'role'

    id = Column(String, unique=True, primary_key=True)
    type = Column(Enum(RoleType), primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # many-to-many relationship between role and user
    role_users = relationship('UserRole', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    users = association_proxy('role_users', 'user', creator=lambda u: UserRole(user=u))

    # many-to-many relationship between role and scope
    role_scopes = relationship('RoleScope', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('role_scopes', 'scope', creator=lambda s: RoleScope(scope=s))

    # many-to-many relationship between role and client
    role_clients = relationship('ClientRole', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    clients = association_proxy('role_clients', 'client', creator=lambda c: ClientRole(client=c))

    # many-to-many relationship between role and project
    role_projects = relationship('ProjectRole', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    projects = association_proxy('role_projects', 'project', creator=lambda p: ProjectRole(project=p))

    # many-to-many relationship between role and provider
    role_providers = relationship('ProviderRole', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    providers = association_proxy('role_providers', 'provider', creator=lambda p: ProviderRole(provider=p))

    def __repr__(self):
        return self._repr('id', 'type', 'name')
