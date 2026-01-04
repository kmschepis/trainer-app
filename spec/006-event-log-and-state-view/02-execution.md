# 006 — Execution Log

## Implemented

- Added Postgres-backed event storage to API.
	- New module: `services/api/app/db.py` (asyncpg pool + table init)
	- New module: `services/api/app/events.py` (minimal projection / reducer)
	- API endpoints in `services/api/app/main.py`:
		- `POST /events` (append-only insert)
		- `GET /state` (read events, project snapshot)
- Updated web to call `GET /state` and render JSON for debugging: `apps/web/app/page.tsx`.
- Added release-notes style summary for this unit: `spec/006-event-log-and-state-view/user-state.md`.

## DB schema

API initializes this table on startup (minimal init strategy, no migrations in this unit):

- `events(id uuid pk, ts timestamptz, type text, session_id text, payload jsonb)`

## Verification

Commands:

- `docker compose up --build -d`
- `curl -s http://localhost:8000/state`
- `curl -s -X POST http://localhost:8000/events -H 'content-type: application/json' -d '{"type":"UserOnboarded","payload":{"goal":"hypertrophy"}}'`
- `curl -s http://localhost:8000/state`

Expected:

- `/events` returns an ack with an `id` and `ts`.
- `/state` returns `meta.eventsCount > 0` and `snapshot.profile` populated after `UserOnboarded`.

Notes:

- `asyncpg` jsonb binding expects JSON to be passed as a string by default; the implementation stores `payload` as `json.dumps(payload)` and uses `$5::jsonb` in SQL.
