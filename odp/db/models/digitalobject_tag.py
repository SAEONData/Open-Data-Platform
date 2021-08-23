from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base


class DigitalObjectTag(Base):
    """Tag instance model, representing a tag attached by a user to
    a digital object.

    The 3-way primary key allows multiple tags of the same type to
    be attached to a given object, but only one such tag per user.
    """

    __tablename__ = 'digitalobject_tag'

    digitalobject_id = Column(String, ForeignKey('digitalobject.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)

    data = Column(JSONB, nullable=False)
    validity = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    digitalobject = relationship('DigitalObject', back_populates='tags')
    tag = relationship('Tag')
    user = relationship('User')
