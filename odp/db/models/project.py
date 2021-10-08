from sqlalchemy import Column, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.project_collection import ProjectCollection


class Project(Base):
    """An organizational entity representing an aggregation of collections
    relevant to a particular SAEON project."""

    __tablename__ = 'project'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # many-to-many relationship between project and collection
    project_collections = relationship('ProjectCollection', back_populates='project', cascade='all, delete-orphan', passive_deletes=True)
    collections = association_proxy('project_collections', 'collection', creator=lambda c: ProjectCollection(collection=c))

    def __repr__(self):
        return self._repr('id', 'name')
