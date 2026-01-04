# 002 — Execution Log

## 2026-01-03

### Changes

- Added Docker Compose stack: `compose.yml`
- Added API service:
  - `services/api/app/main.py` (`GET /health`, `WS /realtime` echo)
  - `services/api/Dockerfile`, `services/api/requirements.txt`
- Added agent placeholder:
  - `services/agent/app/main.py` (`GET /health`)
  - `services/agent/Dockerfile`, `services/agent/requirements.txt`
- Added web app:
  - `apps/web/app/page.tsx` (fetch health + WS echo)
  - `apps/web/Dockerfile`, `apps/web/package.json`, `apps/web/tsconfig.json`
- Added ignores:
  - `.dockerignore`
  - `apps/web/.dockerignore`

### Verification

Commands:

- `docker compose up --build -d`
- `docker compose ps`
- `curl -s http://localhost:8000/health`
- `curl -s http://localhost:9000/health`

Observed:

- Containers started successfully.
- Both health endpoints returned `{ "status": "ok" }`.
- Web container started and served the Phase 0 page.
