import uuid

from flask_login import UserMixin
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import Base
from .member import Member


class User(UserMixin, Base):
    """
    Model representing a user account.
    """
    __tablename__ = 'user'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    superuser = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)
    verified = Column(Boolean, nullable=False)

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
