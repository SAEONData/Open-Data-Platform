from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class ProjectCollection(Base):
    """Model of a project-collection many-to-many relationship, representing
    a collection associated with a project."""

    __tablename__ = 'project_collection'

    project_id = Column(Integer, ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)
    collection_id = Column(Integer, ForeignKey('collection.id', ondelete='CASCADE'), primary_key=True)

    project = relationship('Project', back_populates='project_collections')
    collection = relationship('Collection', back_populates='collection_projects')
