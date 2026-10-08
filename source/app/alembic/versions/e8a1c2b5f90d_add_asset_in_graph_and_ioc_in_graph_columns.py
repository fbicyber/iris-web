"""add asset_in_graph and ioc_in_graph columns

Revision ID: e8a1c2b5f90d
Revises: da626af4a379
Create Date: 2026-04-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8a1c2b5f90d'
down_revision = 'da626af4a379'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ioc', sa.Column('ioc_in_graph', sa.Boolean(), nullable=True))
    op.add_column('case_assets', sa.Column('asset_in_graph', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('case_assets', 'asset_in_graph')
    op.drop_column('ioc', 'ioc_in_graph')

