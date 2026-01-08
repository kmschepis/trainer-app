from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    provider: Mapped[str] = mapped_column(sa.Text, nullable=False)
    provider_subject: Mapped[str] = mapped_column(sa.Text, nullable=False)
    email: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    name: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)


class EventRow(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    ts: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    type: Mapped[str] = mapped_column(sa.Text, nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    session_id: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)


class ProfileRow(Base):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    first_name: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    last_name: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    email: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    goals: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    experience: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    equipment: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    injuries_or_risk_flags: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    diet_prefs: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    metrics_age: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    metrics_height: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    metrics_weight: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    updated_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)


# Keep indexes defined here so Alembic autogenerate can detect them.
sa.Index("users_provider_subject_ux", UserRow.provider, UserRow.provider_subject, unique=True)
sa.Index("events_user_id_idx", EventRow.user_id)
sa.Index("events_user_session_idx", EventRow.user_id, EventRow.session_id)
sa.Index("events_ts_idx", EventRow.ts)
sa.Index("events_type_idx", EventRow.type)

sa.Index("profiles_user_id_ux", ProfileRow.user_id, unique=True)
