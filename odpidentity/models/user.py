import uuid

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from .member import Member


class User(UserMixin, db.Model):
    """
    Model representing a user account.
    """
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    superuser = db.Column(db.Boolean, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    confirmed_at = db.Column(db.DateTime)

    # many-to-many relationship between institution and user represented by member
    members = relationship('Member',
                           back_populates='user',
                           cascade='all, delete-orphan',
                           passive_deletes=True)
    # enables working with the other side of the relationship transparently
    institutions = association_proxy('members', 'institution',
                                     creator=lambda i: Member(institution=i))

    def __repr__(self):
        return '<User %s>' % self.email
