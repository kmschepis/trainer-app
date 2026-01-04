# 002 — Work Items Roadmap

Status: complete (see `02-execution.md`).

## Work items

- [x] Compose stack boots: db + api + web + agent.
- [x] API exposes `GET /health`.
- [x] Agent placeholder exposes `GET /health`.
- [x] API exposes `WS /realtime` echo.
- [x] Web page calls `/health` and exercises WS echo.

## Verification

- `docker compose up --build -d`
- Web `http://localhost:3000`
- API `http://localhost:8000/health`
- Agent `http://localhost:9000/health`
