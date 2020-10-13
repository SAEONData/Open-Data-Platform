from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from odp.db import Base
from odp.db.models.user_privilege import UserPrivilege


class Member(Base):
    """
    Model of a user-institution many-to-many relationship, representing
    a user's membership of an institution.
    """
    __tablename__ = 'member'

    # make user_id the first column of the composite primary key, since
    # auth-related queries typically filter by user_id
    user_id = Column(String, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    # disallow deleting of an institution if it has any members
    institution_id = Column(Integer, ForeignKey('institution.id', ondelete='RESTRICT'), primary_key=True)

    user = relationship('User', back_populates='members')
    institution = relationship('Institution', back_populates='members')

    # many-to-many relationship between member and capability represented by user_privilege
    user_privileges = relationship('UserPrivilege',
                                   back_populates='member',
                                   cascade='all, delete-orphan',
                                   passive_deletes=True)
    # enables working with the other side of the relationship transparently
    capabilities = association_proxy('user_privileges', 'capability',
                                     creator=lambda c: UserPrivilege(capability=c))
