# 002 — Plan

1. Add `compose.yml` with services:
   - `db` (Postgres)
   - `api` (FastAPI)
   - `web` (Next.js)
   - `agent` (placeholder FastAPI)
2. Implement API:
   - `GET /health`
   - `WS /realtime` echo
3. Implement web:
   - Home page fetches `/health`
   - Home page opens WS to `/realtime` and displays echoed message
4. Implement agent:
   - `GET /health`
5. Verify:
   - `docker compose up --build -d`
   - `curl http://localhost:8000/health`
   - Open `http://localhost:3000`
