from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from odp.db import Base
from odp.db.models.privilege import Privilege


class Member(Base):
    """
    Model of an institution-user many-to-many relationship, representing
    a user's membership of an institution.
    """
    __tablename__ = 'member'

    # disallow deleting of an institution if it has any members
    institution_id = Column(Integer, ForeignKey('institution.id', ondelete='RESTRICT'), primary_key=True)
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)

    institution = relationship('Institution', back_populates='members')
    user = relationship('User', back_populates='members')

    # many-to-many relationship between member and capability represented by privilege
    privileges = relationship('Privilege',
                              back_populates='member',
                              cascade='all, delete-orphan',
                              passive_deletes=True)
    # enables working with the other side of the relationship transparently
    capabilities = association_proxy('privileges', 'capability',
                                     creator=lambda c: Privilege(capability=c))
