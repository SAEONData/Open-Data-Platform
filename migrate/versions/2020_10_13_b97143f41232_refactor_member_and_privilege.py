"""Refactor member and privilege

Revision ID: b97143f41232
Revises: f9b7296a76f2
Create Date: 2020-10-13 12:49:19.209149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b97143f41232'
down_revision = 'f9b7296a76f2'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("alter table privilege rename to user_privilege")
    op.execute("alter table user_privilege rename constraint privilege_capability_fkey to user_privilege_capability_fkey")
    op.execute("alter table user_privilege drop constraint privilege_pkey, "
               "add constraint user_privilege_pkey primary key (user_id, institution_id, scope_id, role_id), "
               "drop constraint privilege_member_fkey")
    op.execute("alter table member drop constraint member_pkey, "
               "add constraint member_pkey primary key (user_id, institution_id)")
    op.execute("alter table user_privilege add constraint user_privilege_member_fkey "
               "foreign key (user_id, institution_id) references member on delete cascade")


def downgrade():
    op.execute("alter table user_privilege drop constraint user_privilege_member_fkey")
    op.execute("alter table member drop constraint member_pkey, "
               "add constraint member_pkey primary key (institution_id, user_id)")
    op.execute("alter table user_privilege drop constraint user_privilege_pkey, "
               "add constraint privilege_pkey primary key (institution_id, user_id, scope_id, role_id), "
               "add constraint privilege_member_fkey foreign key (institution_id, user_id) "
               "references member on delete cascade")
    op.execute("alter table user_privilege rename constraint user_privilege_capability_fkey to privilege_capability_fkey")
    op.execute("alter table user_privilege rename to privilege")
