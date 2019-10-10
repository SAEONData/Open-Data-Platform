from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .privilege import Privilege


class Capability(db.Model):
    """
    Model of a scope-role many-to-many relationship, representing the capability
    to perform a particular role within a given application scope.
    """
    scope_id = db.Column(db.Integer, db.ForeignKey('scope.id', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)

    scope = db.relationship('Scope', back_populates='capabilities')
    role = db.relationship('Role', back_populates='capabilities')

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
        return '[{}] {}'.format(self.scope.code, self.role.name)
