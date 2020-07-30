"""Insert scope data

Revision ID: d776f79fab2b
Revises: b1ed6dd977b0
Create Date: 2020-07-29 17:52:31.193242

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd776f79fab2b'
down_revision = 'b1ed6dd977b0'
branch_labels = None
depends_on = None


def upgrade():
    rows = [
        {'key': 'ODP.Admin', 'description': 'Platform administration functions'},
        {'key': 'ODP.Metadata', 'description': 'Metadata management functions'},
        {'key': 'SAEON.Observations.WebAPI', 'description': 'The SAEON Observations Database'},
    ]

    for row in rows:
        key = row['key']
        description = row['description']
        op.execute(f"INSERT INTO scope (key, description) VALUES ('{key}', '{description}') "
                   f"ON CONFLICT DO NOTHING")


def downgrade():
    pass
