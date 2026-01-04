# trainer2

Phase 0 (walking skeleton): Docker Compose brings up Postgres + FastAPI + Next.js + an agent placeholder.

## Run

- `docker compose up --build`

## Endpoints

- Web: http://localhost:3000
- API health: http://localhost:8000/health
- API websocket echo: ws://localhost:8000/realtime
- Agent health: http://localhost:9000/health
