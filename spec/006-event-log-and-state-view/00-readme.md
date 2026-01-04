# 006 — Event Log + State View (Phase 1 foundation)

## Goal

Implement the **append-only event log** and a **materialized state view** so the web UI can render from a single derived snapshot.

## Context

The product spec’s “single source of truth” is an event stream (e.g. `UserOnboarded`, `SetLogged`, `PlanGenerated`). Analytics and UI state derive from these events.

## Acceptance criteria

- API implements `POST /events` to append an event.
- Events are persisted in Postgres (append-only table).
- API implements `GET /state` returning a materialized snapshot for the UI.
- State is reproducible from events (at least for the implemented event types).
- Web can call `GET /state` without needing DB access.

## Non-goals (this unit)

- Auth, multi-user support, advanced relational modeling beyond the event log.
- Full event taxonomy (only what’s needed for subsequent units).
