---
name: phase0-compose-skeleton
description: Scaffold or validate the Phase 0 walking skeleton (Compose + web + api + agent + db) and its boot/health checks. Use when you need a minimal end-to-end stack that runs via `docker compose`.
---

## Mission

Provide the smallest runnable system proving the repo’s service boundaries and basic connectivity.

## When to use (triggers)

- Starting a new repo iteration and need the baseline stack running.
- Phase 0 acceptance checks are failing.
- Adding a new service and want to confirm Compose wiring.

## Inputs

- Root `compose.yml`
- Service directories: `apps/web/`, `services/api/`, `services/agent/`

## Outputs

- `compose.yml` runs services:
  - `db` (Postgres)
  - `api` (FastAPI)
  - `web` (Next.js)
  - `agent` (placeholder)
- Health endpoints:
  - API `GET /health`
  - Agent `GET /health`

## Workflow

1. Ensure Compose services exist and have correct port mappings:
   - web `3000`, api `8000`, agent `9000`, db `5432`.
2. Confirm API implements:
   - `GET /health`
   - `WS /realtime`
3. Confirm web connects to `ws://localhost:8000/realtime`.
4. Verify:
   - `docker compose up --build -d`
   - `docker compose ps`
   - `curl http://localhost:8000/health`
   - `curl http://localhost:9000/health`

## Quality checklist

- One-command boot: `docker compose up --build -d`.
- No extra infra required beyond Docker.
- Web shows a visible WS-connected state.

## Example (from this repo)

- Compose file: `compose.yml`
- API: `services/api/app/main.py`
- Web: `apps/web/app/page.tsx`
