# trainer2

Phase 0 (walking skeleton): Docker Compose brings up Postgres + FastAPI + Next.js + an agent placeholder.

## Run

- `docker compose up --build`

## Chat backends (stub vs LLM)

By default, websocket chat replies come from a built-in stub coach (no LLM).

To route websocket chat through the agent service:

- Set `CHAT_BACKEND=http`

To enable an OpenAI-compatible LLM behind the agent:

- Set `LLM_BACKEND=openai_compatible`
- Set `OPENAI_API_KEY` and `OPENAI_MODEL`
- Optionally set `OPENAI_BASE_URL` (defaults to `https://api.openai.com/v1`)

All variables are documented in `.env.example` (copy to `.env` for local overrides).

## Shortcuts

- `make help`
- `make build`
- `make check`

## Template versioning

- This repo is intended to be taggable as a template release.
- See `git-cheatsheet.md` for the exact commands (e.g. tagging the current commit as `template1`).

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
