"""migrations from cyd iris to dev

Revision ID: b4f7c2d8a9ef
Revises: e0cdb893c68f
Create Date: 2026-06-03 10:13:28.594526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4f7c2d8a9ef'
down_revision = 'e0cdb893c68f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('case_received_file', sa.Column('host', sa.Text(), nullable=True))
    op.add_column('case_received_file', sa.Column('external_id', sa.Text(), nullable=True))
    op.add_column('cases_events', sa.Column('event_end_date', sa.DateTime(), nullable=True))
    op.add_column('cases_events', sa.Column('event_end_date_wtz', sa.DateTime(), nullable=True))
    op.add_column('cases_events', sa.Column('event_end_tz', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('case_received_file', 'host')
    op.drop_column('case_received_file', 'external_id')
    op.drop_column('cases_events', 'event_end_date')
    op.drop_column('cases_events', 'event_end_date_wtz')
    op.drop_column('cases_events', 'event_end_tz')
