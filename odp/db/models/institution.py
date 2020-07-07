from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from odp.db import Base
from odp.db.models.member import Member


class Institution(Base):
    """
    Model representing an institution.
    """
    __tablename__ = 'institution'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)

    # institutions can be hierarchically related
    parent_id = Column(Integer, ForeignKey('institution.id', ondelete='CASCADE'))
    parent = relationship('Institution',
                          backref='children',
                          remote_side=[id],
                          primaryjoin=parent_id == id)

    # many-to-many relationship between institution and user represented by member
    members = relationship('Member',
                           back_populates='institution',
                           cascade='all, delete-orphan',
                           passive_deletes=True)
    # enables working with the other side of the relationship transparently
    users = association_proxy('members', 'user',
                              creator=lambda u: Member(user=u))

    def __repr__(self):
        return '<Institution %s>' % self.key
