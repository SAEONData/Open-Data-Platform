"""Insert capabilities data

Revision ID: c967263958b7
Revises: d776f79fab2b
Create Date: 2020-07-30 07:33:11.144051

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c967263958b7'
down_revision = 'd776f79fab2b'
branch_labels = None
depends_on = None


def upgrade():
    capabilities = {
        'ODP.Admin': ['admin', 'member'],
        'ODP.Metadata': ['curator', 'contributor', 'member'],
        'SAEON.Observations.WebAPI': ['admin', 'contributor'],
    }

    for scope, roles in capabilities.items():
        for role in roles:
            op.execute("INSERT INTO capability (scope_id, role_id) "
                       "SELECT s.id, r.id FROM scope s, role r "
                       f"WHERE s.key = '{scope}' AND r.key = '{role}' "
                       "ON CONFLICT DO NOTHING")


def downgrade():
    pass
