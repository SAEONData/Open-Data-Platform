from sqlalchemy import Column, Integer, String, ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from . import Base
from .member import Member


class Institution(Base):
    """
    Model representing an institution.
    """
    __tablename__ = 'institution'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    # institutions can be hierarchically related
    parent_id = Column(Integer)
    parent = relationship('Institution',
                          backref='children',
                          remote_side=[id],
                          primaryjoin=parent_id == id)

    registry_id = Column(Integer, ForeignKey('institution_registry.id', ondelete='CASCADE'), nullable=False)
    registry = relationship('InstitutionRegistry', back_populates='institutions')

    __table_args__ = (
        # ensure that hierarchically-related institutions are in the same registry
        UniqueConstraint('id', 'registry_id'),
        ForeignKeyConstraint(
            ('parent_id', 'registry_id'),
            ('institution.id', 'institution.registry_id'),
            ondelete='CASCADE',
        ),
    )

    # many-to-many relationship between institution and user represented by member
    members = relationship('Member',
                           back_populates='institution',
                           cascade='all, delete-orphan',
                           passive_deletes=True)
    # enables working with the other side of the relationship transparently
    users = association_proxy('members', 'user',
                              creator=lambda u: Member(user=u))

    def __repr__(self):
        return '<Institution %s>' % self.code
