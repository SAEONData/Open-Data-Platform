from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .actor import Actor


class Capability(db.Model):
    """
    Model of a scope-role many-to-many relationship, representing the capability
    to perform a particular role within a given application scope.
    """
    id = db.Column(db.Integer, primary_key=True)

    scope_id = db.Column(db.Integer, db.ForeignKey('scope.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))

    scope = db.relationship('Scope', back_populates='capabilities')
    role = db.relationship('Role', back_populates='capabilities')

    __table_args__ = (
        db.UniqueConstraint('scope_id', 'role_id'),
    )

    # many-to-many relationship between member and capability represented by actor
    actors = relationship('Actor',
                          back_populates='capability',
                          cascade='all, delete-orphan',
                          passive_deletes=True)
    # enables working with the other side of the relationship transparently
    members = association_proxy('actors', 'member',
                                creator=lambda m: Actor(member=m))

    @property
    def label(self):
        return '[{}] {}'.format(self.scope.code, self.role.name)
