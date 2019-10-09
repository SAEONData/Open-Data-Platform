from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .actor import Actor


class Member(db.Model):
    """
    Model of an institution-user many-to-many relationship, representing
    a user's membership of an institution.
    """
    # disallow deleting of an institution if it has any members
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id', ondelete='RESTRICT'), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)

    institution = db.relationship('Institution', back_populates='members')
    user = db.relationship('User', back_populates='members')

    # many-to-many relationship between member and capability represented by actor
    actors = relationship('Actor',
                          back_populates='member',
                          cascade='all, delete-orphan',
                          passive_deletes=True)
    # enables working with the other side of the relationship transparently
    capabilities = association_proxy('actors', 'capability',
                                     creator=lambda c: Actor(capability=c))
