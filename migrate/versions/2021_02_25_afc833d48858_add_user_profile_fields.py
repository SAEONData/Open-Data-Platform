"""Add user profile fields

Revision ID: afc833d48858
Revises: b3fca062a45e
Create Date: 2021-02-25 11:42:33.173756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afc833d48858'
down_revision = 'b3fca062a45e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic ###
    op.add_column('user', sa.Column('family_name', sa.String(), nullable=True))
    op.add_column('user', sa.Column('given_name', sa.String(), nullable=True))
    op.add_column('user', sa.Column('picture', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic ###
    op.drop_column('user', 'picture')
    op.drop_column('user', 'given_name')
    op.drop_column('user', 'family_name')
    # ### end Alembic commands ###
