"""Add local timezone to case

Revision ID: e0cdb893c68f
Revises: 29dbabc6d9ff
Create Date: 2025-03-25 15:45:56.413776

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from app.alembic.alembic_utils import _table_has_column

# revision identifiers, used by Alembic.
revision = 'e0cdb893c68f'
down_revision = '29dbabc6d9ff'
branch_labels = None
depends_on = None


def upgrade():
    # Add column local_timezone to Case if it doesn't exist
    if not _table_has_column('cases', 'local_timezone'):
        op.add_column('cases',
                      sa.Column('local_timezone', sa.Text)
                    )


def downgrade():
    pass
