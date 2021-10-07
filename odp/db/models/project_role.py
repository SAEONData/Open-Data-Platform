from sqlalchemy import Column, String, ForeignKey, ForeignKeyConstraint, Enum, CheckConstraint
from sqlalchemy.orm import relationship

from odp.db import Base
from odp.db.models.types import RoleType


class ProjectRole(Base):
    """Model of a many-to-many project-role association."""

    __tablename__ = 'project_role'

    __table_args__ = (
        ForeignKeyConstraint(
            ('role_id', 'role_type'),
            ('role.id', 'role.type'),
            name='project_role_role_fkey',
            ondelete='CASCADE',
        ),
        CheckConstraint(
            f"role_type = '{RoleType.PROJECT}'",
            name='project_role_role_type_check',
        ),
    )

    project_id = Column(String, ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(String, primary_key=True)
    role_type = Column(Enum(RoleType), primary_key=True)

    project = relationship('Project', back_populates='project_roles')
    role = relationship('Role', back_populates='role_projects')
