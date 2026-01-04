# User State

## Current Functionality

- The stack boots via Docker Compose and the web UI loads and connects to the API.
- The web UI supports a basic chat loop over WebSocket with session creation and agent responses.
- The API provides an append-only event log and a derived `/state` snapshot for UI reads.

## How To Use

- Run `make up` (or `make run`) and open `http://localhost:3000`.
- Append events via `POST http://localhost:8000/events` and view the projection at `GET http://localhost:8000/state`.
- View metrics and traces via Grafana at `http://localhost:3001`.

## Known Limits

- There is no auth or multi-user model yet, so events are global to the system.
- The `/state` projection supports only a small starter set of event types and is intended to evolve.
- The web UI is a debug-first surface and does not yet render the full “canvas” UX.
