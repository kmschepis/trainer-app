"""add password_hash to users

Revision ID: 0004_add_password_hash_to_users
Revises: 0003_create_profiles_table
Create Date: 2026-01-06

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_add_password_hash_to_users"
down_revision = "0003_create_profiles_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_hash")
