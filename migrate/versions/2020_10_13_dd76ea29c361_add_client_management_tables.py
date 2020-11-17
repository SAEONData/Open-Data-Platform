"""Add client management tables

Revision ID: dd76ea29c361
Revises: b97143f41232
Create Date: 2020-10-13 15:11:11.559483

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'dd76ea29c361'
down_revision = 'b97143f41232'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic ###
    op.create_table('client',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('key', sa.String(), nullable=False),
                    sa.Column('institution_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['institution_id'], ['institution.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('key')
                    )
    op.create_table('client_capability',
                    sa.Column('client_id', sa.Integer(), nullable=False),
                    sa.Column('scope_id', sa.Integer(), nullable=False),
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['scope_id', 'role_id'], ['capability.scope_id', 'capability.role_id'],
                                            name='client_capability_capability_fkey', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('client_id', 'scope_id', 'role_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic ###
    op.drop_table('client_capability')
    op.drop_table('client')
    # ### end Alembic commands ###