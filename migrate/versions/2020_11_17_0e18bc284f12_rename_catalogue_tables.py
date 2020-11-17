"""Rename catalogue tables

Revision ID: 0e18bc284f12
Revises: 1e51009ae3c6
Create Date: 2020-11-17 17:14:08.463392

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0e18bc284f12'
down_revision = '1e51009ae3c6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("alter table metadata_status rename to catalogue_record")
    op.execute("alter index metadata_status_pkey rename to catalogue_record_pkey")
    op.execute("alter index ix_metadata_status_created_metadata_id rename to ix_catalogue_record_created_metadata_id")
    op.execute("alter table datacite_status rename constraint datacite_status_metadata_id_fkey to datacite_record_metadata_id_fkey")
    op.execute("alter table datacite_status rename to datacite_record")
    op.execute("alter index datacite_status_pkey rename to datacite_record_pkey")
    op.execute("alter index datacite_status_doi_key rename to datacite_record_doi_key")


def downgrade():
    op.execute("alter table catalogue_record rename to metadata_status")
    op.execute("alter index catalogue_record_pkey rename to metadata_status_pkey")
    op.execute("alter index ix_catalogue_record_created_metadata_id rename to ix_metadata_status_created_metadata_id")
    op.execute("alter table datacite_record rename constraint datacite_record_metadata_id_fkey to datacite_status_metadata_id_fkey")
    op.execute("alter table datacite_record rename to datacite_status")
    op.execute("alter index datacite_record_pkey rename to datacite_status_pkey")
    op.execute("alter index datacite_record_doi_key rename to datacite_status_doi_key")
