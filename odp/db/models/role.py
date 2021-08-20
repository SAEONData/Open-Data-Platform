from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.role_scope import RoleScope
from odp.db.models.user_role import UserRole


class Role(Base):
    """Model representing a person's role within SAEON, or
    the role of a person (SAEON or external) with respect to
    a particular project and/or provider.

    If a role is linked with a project and/or provider, then
    any assigned scopes grant access only to resources linked
    with that project and/or provider.
    """

    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    project_id = Column(Integer, ForeignKey('project.id', ondelete='CASCADE'))
    project = relationship('Project', back_populates='roles')

    provider_id = Column(Integer, ForeignKey('provider.id', ondelete='CASCADE'))
    provider = relationship('Provider', back_populates='roles')

    # many-to-many relationship between role and user
    role_users = relationship('UserRole', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    users = association_proxy('role_users', 'user', creator=lambda u: UserRole(user=u))

    # many-to-many relationship between role and scope
    role_scopes = relationship('RoleScope', back_populates='role', cascade='all, delete-orphan', passive_deletes=True)
    scopes = association_proxy('role_scopes', 'scope', creator=lambda s: RoleScope(scope=s))

    def __repr__(self):
        return self._repr('id', 'key', 'name', 'project', 'provider')
