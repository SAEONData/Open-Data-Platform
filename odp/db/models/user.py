import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.user_role import UserRole


class User(Base):
    """A user account."""

    __tablename__ = 'user'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    active = Column(Boolean, nullable=False)
    verified = Column(Boolean, nullable=False)
    name = Column(String)
    picture = Column(String)

    # many-to-many user_role entities are persisted by
    # assigning/removing Role instances to/from roles
    user_roles = relationship('UserRole', cascade='all, delete-orphan', passive_deletes=True)
    roles = association_proxy('user_roles', 'role', creator=lambda r: UserRole(role=r))

    _repr_ = 'id', 'email', 'name', 'active', 'verified'
