from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventRow(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    ts: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    type: Mapped[str] = mapped_column(sa.Text, nullable=False)
    session_id: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)


# Keep indexes defined here so Alembic autogenerate can detect them.
sa.Index("events_ts_idx", EventRow.ts)
sa.Index("events_type_idx", EventRow.type)
