from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.project_collection import ProjectCollection


class Project(Base):
    """An organizational entity representing an aggregation of collections
    relevant to a particular SAEON project.

    Project-specific roles permit scope access to only those collections
    that are linked with the specified project.
    """

    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    # one-to-many relationship with role
    roles = relationship('Role', back_populates='project', cascade='all, delete-orphan', passive_deletes=True)

    # many-to-many relationship between project and collection
    project_collections = relationship('ProjectCollection', back_populates='project', cascade='all, delete-orphan', passive_deletes=True)
    collections = association_proxy('project_collections', 'collection', creator=lambda c: ProjectCollection(collection=c))

    def __repr__(self):
        return self._repr('id', 'key', 'name')
