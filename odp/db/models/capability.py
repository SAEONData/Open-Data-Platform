from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from odp.db import Base
from odp.db.models.privilege import Privilege


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

    # many-to-many relationship between member and capability represented by privilege
    privileges = relationship('Privilege',
                              back_populates='capability',
                              cascade='all, delete-orphan',
                              passive_deletes=True)
    # enables working with the other side of the relationship transparently
    members = association_proxy('privileges', 'member',
                                creator=lambda m: Privilege(member=m))

    @property
    def label(self):
        return '[{}] {}'.format(self.scope.key, self.role.name)
