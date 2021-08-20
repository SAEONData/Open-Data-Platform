from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from odp.db import Base


class Project(Base):
    """An organizational entity representing an aggregation of collections
    relevant to a particular SAEON project.

    Project-specific roles and clients permit scope access to only those
    collections that are linked with the specified project.
    """

    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    # one-to-many relationship with role
    roles = relationship('Role', back_populates='project', cascade='all, delete-orphan', passive_deletes=True)

    # one-to-many relationship with client
    clients = relationship('Client', back_populates='project', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return '<Project %s>' % self.key
