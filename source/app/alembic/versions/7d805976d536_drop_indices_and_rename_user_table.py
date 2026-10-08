"""drop indices and rename user table

Revision ID: 7d805976d536
Revises: b4f7c2d8a9ef
Create Date: 2026-04-21 11:36:51.727102

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '7d805976d536'
down_revision = 'b4f7c2d8a9ef'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text('DROP INDEX IF EXISTS idx_case_assets_case_id;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_case_assets_date_added;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_case_assets_date_update;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_case_assets_name;'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_alert_case_association_case_id;'))
    op.execute(sa.text('DROP INDEX IF EXISTS ix_case_tags_tag_id;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_ioc_tags;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_ioc_value_hash;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_alerts_creation_time;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_alert_source_ref;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_alerts_customer_id;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_alerts_source_event_time;'))
    op.execute(sa.text('DROP INDEX IF EXISTS idx_alerts_title;'))
    # if a new database is created, the table will already be named usersa
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if 'user' in tables and 'users' not in tables:
        op.rename_table('user', 'users')

def downgrade():
    pass
