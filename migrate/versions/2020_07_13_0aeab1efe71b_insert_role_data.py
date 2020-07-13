"""Insert role data

Revision ID: 0aeab1efe71b
Revises: f11e224a11f5
Create Date: 2020-07-13 11:33:20.768034

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0aeab1efe71b'
down_revision = 'f11e224a11f5'
branch_labels = None
depends_on = None


def upgrade():
    rows = [
        {'key': 'admin', 'name': 'Admin'},
        {'key': 'curator', 'name': 'Curator'},
        {'key': 'contributor', 'name': 'Contributor'},
        {'key': 'member', 'name': 'Member'},
    ]

    for row in rows:
        key = row['key']
        name = row['name']
        op.execute(f"INSERT INTO role (key, name) VALUES ('{key}', '{name}') "
                   f"ON CONFLICT DO NOTHING")


def downgrade():
    pass
