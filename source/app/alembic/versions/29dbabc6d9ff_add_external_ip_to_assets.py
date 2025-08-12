"""Add external IP to assets

Revision ID: 29dbabc6d9ff
Revises: d5a720d1b99b
Create Date: 2024-03-19 17:46:27.602224

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from app.alembic.alembic_utils import _table_has_column


# revision identifiers, used by Alembic.
revision = '29dbabc6d9ff'
down_revision = 'd5a720d1b99b'
branch_labels = None
depends_on = None


def upgrade():
    # Now issue changes on existing tables and migrate Asset external_ip
    # Add column asset_external_ip to CaseAssets if not existing
    if not _table_has_column('case_assets', 'asset_external_ip'):
        op.add_column('case_assets',
                      sa.Column('asset_external_ip', sa.Text)
                      )



def downgrade():
    pass