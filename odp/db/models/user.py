import uuid

from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.user_role import UserRole


class User(Base):
    """User account model."""

    __tablename__ = 'user'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    active = Column(Boolean, nullable=False)
    verified = Column(Boolean, nullable=False)
    name = Column(String)
    picture = Column(String)

    # many-to-many relationship between user and role
    user_roles = relationship('UserRole', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)
    roles = association_proxy('user_roles', 'role', creator=lambda r: UserRole(role=r))

    def __repr__(self):
        return self._repr('id', 'email', 'name', 'active', 'verified')

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
        return self.id

    # endregion
