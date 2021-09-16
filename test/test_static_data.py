from sqlalchemy import select

from odp.api.models.auth import SystemScope
from odp.db import Session
from odp.db.models import Role, Scope, RoleScope


def test_system_scopes(static_data):
    result = Session.execute(select(Scope.key))
    assert result.scalars().all() == [s.value for s in SystemScope]


def test_sysadmin_role(static_data):
    result = Session.execute(select(Role))
    assert result.scalar_one().key == 'sysadmin'
    result = Session.execute(select(
        RoleScope, Role.key.label('role_key'), Scope.key.label('scope_key')
    ).join(Role).join(Scope))
    assert [(row.role_key, row.scope_key) for row in result] == [('sysadmin', s.value) for s in SystemScope]
