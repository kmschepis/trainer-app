# 006 — Execution Log

## Implemented

- Added Postgres-backed event storage to API and a materialized `/state` view.
	- Projection/reducer: `services/api/app/events.py`
	- HTTP routes: `services/api/app/routes/events.py`
- Migrated schema management to Alembic migrations (no runtime DDL):
	- `services/api/alembic.ini`, `services/api/alembic/env.py`
	- Initial migration creates `events` table + indexes: `services/api/alembic/versions/0001_create_events_table.py`
	- API runs `alembic upgrade head` on container start: `services/api/entrypoint.sh`
- Migrated runtime DB access away from raw SQL to SQLAlchemy async with a repository/UoW pattern:
	- Session/engine: `services/api/app/db.py`
	- ORM model: `services/api/app/models.py`
	- Repository: `services/api/app/repositories/events_repo.py`
	- Unit of Work + deps: `services/api/app/uow.py`, `services/api/app/deps.py`
- Persisted websocket chat messages as events:
	- `ChatMessageSent` is appended for both user + assistant messages via `services/api/app/services/chat_service.py`.

## DB schema

Alembic manages this schema (initial migration):

- `events(id uuid pk, ts timestamptz, type text, session_id text, payload jsonb)`
- indexes: `events_ts_idx`, `events_type_idx`

## Verification

Commands:

- `docker compose up --build -d`
- `docker compose run --rm api alembic upgrade head`
- `curl -s http://localhost:8000/state`
- `curl -s -X POST http://localhost:8000/events -H 'content-type: application/json' -d '{"type":"UserOnboarded","payload":{"goal":"hypertrophy"}}'`
- `curl -s http://localhost:8000/state`

Expected:

- `/events` returns an ack with an `id` and `ts`.
- `/state` returns `meta.eventsCount > 0` and `snapshot.profile` populated after `UserOnboarded`.

Notes:

- Event persistence is now via SQLAlchemy async ORM (no raw SQL required in runtime handlers).
