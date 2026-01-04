"""create events table

Revision ID: 0001_create_events_table
Revises:
Create Date: 2026-01-04

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_create_events_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("session_id", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )

    op.create_index("events_ts_idx", "events", ["ts"], unique=False)
    op.create_index("events_type_idx", "events", ["type"], unique=False)


def downgrade() -> None:
    op.drop_index("events_type_idx", table_name="events")
    op.drop_index("events_ts_idx", table_name="events")
    op.drop_table("events")
