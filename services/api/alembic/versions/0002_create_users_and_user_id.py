"""create users table and add events.user_id

Revision ID: 0002_create_users_and_user_id
Revises: 0001_create_events_table
Create Date: 2026-01-05

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_create_users_and_user_id"
down_revision = "0001_create_events_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("provider_subject", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("provider", "provider_subject", name="users_provider_subject_ux"),
    )

    op.add_column("events", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))

    op.create_index("events_user_id_idx", "events", ["user_id"], unique=False)
    op.create_index("events_user_session_idx", "events", ["user_id", "session_id"], unique=False)


def downgrade() -> None:
    op.drop_index("events_user_session_idx", table_name="events")
    op.drop_index("events_user_id_idx", table_name="events")

    op.drop_column("events", "user_id")

    op.drop_table("users")
