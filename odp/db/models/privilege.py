from sqlalchemy import Column, Integer, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from . import Base


class Privilege(Base):
    """
    Model of a member-capability relationship (institution-user-scope-role),
    representing the privilege assigned to a member to use a particular capability.
    """
    __tablename__ = 'privilege'

    institution_id = Column(Integer, primary_key=True)
    user_id = Column(String, primary_key=True)
    scope_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)

    member = relationship('Member', back_populates='privileges')
    capability = relationship('Capability', back_populates='privileges')

    __table_args__ = (
        ForeignKeyConstraint(
            ('institution_id', 'user_id'),
            ('member.institution_id', 'member.user_id'),
            name='privilege_member_fkey',
            ondelete='CASCADE',
        ),
        ForeignKeyConstraint(
            ('scope_id', 'role_id'),
            ('capability.scope_id', 'capability.role_id'),
            name='privilege_capability_fkey',
            ondelete='CASCADE',
        ),
    )

    institution = relationship('Institution', viewonly=True, foreign_keys=institution_id, primaryjoin='Privilege.institution_id == Institution.id')
    user = relationship('User', viewonly=True, foreign_keys=user_id, primaryjoin='Privilege.user_id == User.id')
    scope = relationship('Scope', viewonly=True, foreign_keys=scope_id, primaryjoin='Privilege.scope_id == Scope.id')
    role = relationship('Role', viewonly=True, foreign_keys=role_id, primaryjoin='Privilege.role_id == Role.id')
