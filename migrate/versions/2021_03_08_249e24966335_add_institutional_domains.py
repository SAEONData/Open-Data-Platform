"""Add institutional domains

Revision ID: 249e24966335
Revises: d378fac89192
Create Date: 2021-03-08 08:36:07.309843

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '249e24966335'
down_revision = 'd378fac89192'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic ###
    op.create_table('domain',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('institution_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['institution_id'], ['institution.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic ###
    op.drop_table('domain')
    # ### end Alembic commands ###