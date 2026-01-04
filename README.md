# trainer2

Phase 0 (walking skeleton): Docker Compose brings up Postgres + FastAPI + Next.js + an agent placeholder.

## Run

- `docker compose up --build`

## Database migrations (Alembic)

The API uses Alembic for schema migrations.

On `docker compose up`, the API container automatically runs `alembic upgrade head` before starting.

- Apply migrations: `docker compose run --rm api alembic upgrade head`
- Create a new migration (after model changes): `docker compose run --rm api alembic revision -m "..." --autogenerate`

For a destructive reset (wipe DB volume + re-migrate), see [.dev/scripts/README.md](.dev/scripts/README.md).

## Chat (how it works)

The web app connects to the API websocket (`/realtime`). When you send a chat message:

- Browser (Next.js) -> API websocket `/realtime`
- API -> agent service `POST /respond`
- Agent -> OpenAI-compatible Chat Completions API

To run chat, set these in `.env` (see `.env.example`):

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- Optional: `OPENAI_BASE_URL` (defaults to `https://api.openai.com/v1`)

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
