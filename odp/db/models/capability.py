from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.client_capability import ClientCapability
from odp.db.models.user_privilege import UserPrivilege


class Capability(Base):
    """
    Model of a scope-role many-to-many relationship, representing the capability
    to perform a particular role within a given application scope.
    """
    __tablename__ = 'capability'

    scope_id = Column(Integer, ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)

    scope = relationship('Scope', back_populates='capabilities')
    role = relationship('Role', back_populates='capabilities')

    # many-to-many relationship between member and capability represented by user_privilege
    user_privileges = relationship('UserPrivilege',
                                   back_populates='capability',
                                   cascade='all, delete-orphan',
                                   passive_deletes=True)
    # enables working with the other side of the relationship transparently
    members = association_proxy('user_privileges', 'member',
                                creator=lambda m: UserPrivilege(member=m))

    # many-to-many relationship between client and capability represented by client_capability
    client_capabilities = relationship('ClientCapability',
                                       back_populates='capability',
                                       cascade='all, delete-orphan',
                                       passive_deletes=True)
    # enables working with the other side of the relationship transparently
    clients = association_proxy('client_capabilities', 'client',
                                creator=lambda c: ClientCapability(client=c))

    @property
    def label(self):
        return '[{}] {}'.format(self.scope.key, self.role.name)
