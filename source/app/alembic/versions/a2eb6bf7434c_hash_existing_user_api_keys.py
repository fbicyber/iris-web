"""hash existing user api keys

Revision ID: a2eb6bf7434c
Revises: f3c9a1d4b8e2
Create Date: 2026-09-17 00:00:00.000000

"""
import hashlib

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2eb6bf7434c'
down_revision = 'f3c9a1d4b8e2'
branch_labels = None
depends_on = None


def upgrade():
    # Existing api_key values are stored in plaintext. Re-hash them in place so the
    # column only ever holds a SHA-256 digest going forward; existing keys keep working
    # since authentication now hashes the presented key before comparing.
    conn = op.get_bind()
    users = conn.execute(sa.text('SELECT id, api_key FROM users WHERE api_key IS NOT NULL')).fetchall()

    for user_id, api_key in users:
        hashed = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
        conn.execute(
            sa.text('UPDATE users SET api_key = :hashed WHERE id = :user_id'),
            {'hashed': hashed, 'user_id': user_id}
        )


def downgrade():
    # Irreversible: the original plaintext API keys cannot be recovered from their hash.
    pass
