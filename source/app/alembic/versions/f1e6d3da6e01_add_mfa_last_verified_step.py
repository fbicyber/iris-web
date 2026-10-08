"""add mfa_last_verified_step to users

Revision ID: f1e6d3da6e01
Revises: a2eb6bf7434c
Create Date: 2026-09-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1e6d3da6e01'
down_revision = 'a2eb6bf7434c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('mfa_last_verified_step', sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column('users', 'mfa_last_verified_step')
