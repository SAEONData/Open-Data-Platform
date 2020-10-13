from sqlalchemy import Column, Integer, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from odp.db import Base


class UserPrivilege(Base):
    """
    Model of a member-capability relationship (user-institution-scope-role),
    representing the privilege granted to a user to use a capability on
    behalf of an institution.

    A privilege may be thought of as an institution-scope-role tuple.
    """
    __tablename__ = 'user_privilege'

    user_id = Column(String, primary_key=True)
    institution_id = Column(Integer, primary_key=True)
    scope_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)

    member = relationship('Member', back_populates='user_privileges')
    capability = relationship('Capability', back_populates='user_privileges')

    __table_args__ = (
        ForeignKeyConstraint(
            ('user_id', 'institution_id'),
            ('member.user_id', 'member.institution_id'),
            name='user_privilege_member_fkey',
            ondelete='CASCADE',
        ),
        ForeignKeyConstraint(
            ('scope_id', 'role_id'),
            ('capability.scope_id', 'capability.role_id'),
            name='user_privilege_capability_fkey',
            ondelete='CASCADE',
        ),
    )

    user = relationship(
        'User',
        viewonly=True,
        foreign_keys=user_id,
        primaryjoin='UserPrivilege.user_id == User.id',
    )
    institution = relationship(
        'Institution',
        viewonly=True,
        foreign_keys=institution_id,
        primaryjoin='UserPrivilege.institution_id == Institution.id',
    )
    scope = relationship(
        'Scope',
        viewonly=True,
        foreign_keys=scope_id,
        primaryjoin='UserPrivilege.scope_id == Scope.id',
    )
    role = relationship(
        'Role',
        viewonly=True,
        foreign_keys=role_id,
        primaryjoin='UserPrivilege.role_id == Role.id',
    )
