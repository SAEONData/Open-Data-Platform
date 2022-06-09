from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from odp.db import Base


class ProjectCollection(Base):
    """Model of a many-to-many project-collection association."""

    __tablename__ = 'project_collection'

    project_id = Column(String, ForeignKey('project.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    collection_id = Column(String, ForeignKey('collection.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)

    project = relationship('Project', viewonly=True)
    collection = relationship('Collection')
