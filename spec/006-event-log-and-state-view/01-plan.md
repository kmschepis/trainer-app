# 006 — Plan

1. Define a minimal event envelope (server-side):
   - `id`, `ts`, `type`, `payload` (JSON), optional `sessionId`.
2. Add Postgres storage:
   - `events` table (append-only).
   - minimal initialization strategy (keep it aligned with repo conventions).
3. Implement `POST /events`:
   - validate type + payload
   - insert row
   - return ack with event id
4. Implement basic projection logic:
   - for known event types, reduce into a state dict
5. Implement `GET /state`:
   - read events
   - project state
   - return JSON
6. Verify with:
   - `docker compose up --build -d`
   - curl `POST /events` and confirm `GET /state` updates
