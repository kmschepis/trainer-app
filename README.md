# trainer2

Phase 0 (walking skeleton): Docker Compose brings up Postgres + FastAPI + Next.js + an agent placeholder.

## Run

- `docker compose up --build`

## Endpoints

- Web: http://localhost:3000
- API health: http://localhost:8000/health
- API websocket echo: ws://localhost:8000/realtime
- Agent health: http://localhost:9000/health

## Observability

- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- Loki: http://localhost:3100
- Tempo: http://localhost:3200

Metrics:

- API metrics: http://localhost:8000/metrics
- Agent metrics: http://localhost:9000/metrics
