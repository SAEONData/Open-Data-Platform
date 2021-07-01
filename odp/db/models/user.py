import uuid

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from odp.db import Base
from odp.db.models.member import Member


class User(Base):
    """
    Model representing a user account.
    """
    __tablename__ = 'user'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    superuser = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)
    verified = Column(Boolean, nullable=False)
    name = Column(String)
    picture = Column(String)

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

    # region Flask-Login

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active and self.verified

    def get_id(self):
        return str(self.id)

    # endregion
