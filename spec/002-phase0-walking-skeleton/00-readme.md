# 002 — Phase 0: Walking Skeleton

## Goal

Prove the end-to-end stack boots via Docker Compose:

- Web loads
- API responds to `/health`
- WebSocket echo works end-to-end
- Agent placeholder boots cleanly

## Acceptance criteria

- `docker compose up --build -d` brings up all services without errors.
- Web is reachable at `http://localhost:3000`.
- API health returns `{"status":"ok"}` at `http://localhost:8000/health`.
- Agent health returns `{"status":"ok"}` at `http://localhost:9000/health`.
- Web page connects to `ws://localhost:8000/realtime` and shows an echoed message.

## Implementation notes

- Phase 0 is intentionally minimal: no auth, migrations, event schema, or persistence beyond Postgres boot.
- The API owns the WebSocket endpoint; the web client connects directly to the API.
