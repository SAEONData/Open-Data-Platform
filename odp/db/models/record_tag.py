from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, ForeignKeyConstraint, Integer, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import AuditCommand, TagType


class RecordTag(Base):
    """Tag instance model, representing a tag attached by a user to
    a record.

    Multiple instances of the same tag id may be attached to a given
    record, but only one such tag per user.

    user_id is nullable to allow tags to be set by the system.
    """

    __tablename__ = 'record_tag'

    __table_args__ = (
        UniqueConstraint('record_id', 'tag_id', 'user_id'),
        ForeignKeyConstraint(
            ('tag_id', 'tag_type'), ('tag.id', 'tag.type'),
            name='record_tag_tag_fkey', ondelete='CASCADE',
        ),
        CheckConstraint(
            f"tag_type = '{TagType.record}'",
            name='record_tag_tag_type_check',
        ),
    )

    id = Column(Integer, primary_key=True)
    record_id = Column(String, ForeignKey('record.id', ondelete='CASCADE'), nullable=False)
    tag_id = Column(String, nullable=False)
    tag_type = Column(Enum(TagType), nullable=False)
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'))

    data = Column(JSONB, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    record = relationship('Record')
    tag = relationship('Tag')
    user = relationship('User')


class RecordTagAudit(Base):
    """Record tag audit log."""

    __tablename__ = 'record_tag_audit'

    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)
    user_id = Column(String)
    command = Column(Enum(AuditCommand), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    _record_id = Column(String, nullable=False)
    _tag_id = Column(String, nullable=False)
    _user_id = Column(String)
    _data = Column(JSONB)
