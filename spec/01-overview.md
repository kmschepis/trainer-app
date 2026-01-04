# Project Overview + Roadmap (Trainer2)

## What this repo is

`trainer2` is a container-first, spec-driven foundation for an **agentic AI personal trainer**.

It intentionally separates concerns:

- **Web (Next.js)**: user UI (chat + “canvas” panels)
- **API (FastAPI)**: system boundary + persistence + realtime gateway
- **Agent (FastAPI)**: LLM-backed coach logic (replaceable intelligence)
- **DB (Postgres)**: durable storage

A key architectural constraint is **auditability**: the system should be explainable, reproducible, and safe.

## How it works (high level)

### Runtime architecture

- The browser connects to the **API** over WebSocket at `ws://localhost:8000/realtime`.
- The user sends messages using a JSON envelope (e.g. `chat.send`).
- The **API** forwards relevant requests to the **agent** over HTTP.
- The agent returns:
  - assistant chat text
  - optional **A2UI actions** (UI mutations)
  - later: plan diffs and structured coaching outputs
- The API relays responses to the browser.

### Data model philosophy (MVP direction)

The product spec calls for an **append-only event log** as the single source of truth:

- Web/API write **events** (e.g. `UserOnboarded`, `SetLogged`)
- The API builds a **materialized view** (`/state`) for the UI
- Analytics (fatigue, trends) are derived from events

This makes plan changes explainable and supports “diff-first” coaching.

### UI philosophy (Chat + Canvas)

The user experience is a combination of:

- **Chat**: free-form logging + coaching conversation
- **Canvas**: structured panels driven by agent-emitted actions (A2UI)

In MVP terms, the canvas is simply a deterministic UI state machine: the agent emits actions like `ui.create` / `ui.update`, and the web renders panels accordingly.

### Observability baseline

Local dev includes a production-shaped observability stack:

- **Prometheus** scrapes API + agent metrics
- **OTel Collector** ingests logs/traces
- **Loki** stores logs
- **Tempo** stores traces
- **Grafana** provides a unified UI

## Spec workflow (authoritative)

Work is done in **numbered units** under `spec/NNN-kebab-case/`, each with:

- `00-readme.md` (user story + acceptance criteria)
- `01-plan.md` (step-by-step plan)
- `02-execution.md` (running log of what was actually done)

## Roadmap summary

### Done (implemented)

- **001 Init**: initial product/architecture spec captured.
- **002 Phase 0**: walking skeleton boots via Docker Compose; API `/health`; WS echo; web page checks.
- **003 WS Ready**: JSON envelope; API→agent chat; minimal chat UI.
- **004 Observability**: Prometheus + Grafana + Loki + Tempo + OTel Collector; metrics/logs/traces wired.
- **005 Template hardening**: CI + dependabot + `.env.example` + linting baseline.

### Next (to reach the “current project” MVP from `001-Initial_plan.md`)

The next units are scaffolds for Phase 1/2 in the product plan (events → onboarding → plan → workout canvas → weekly review → plan diffs → fatigue math).

- **006 Event log + state view**: append-only events + `/state` materialization.
- **007 Onboarding (core loop)**: onboarding form → events → state.
- **008 Plan generation (agent)**: agent generates 1-week plan markdown; persisted as events.
- **009 Workout canvas + set logging**: workout view (markdown plan + set logger), `SetLogged` events.
- **010 Weekly review**: weekly summary report + simple charts derived from state.
- **011 Plan diff proposal/accept**: diff panel + Accept/Modify/Deny actions; diff events.
- **012 Fatigue analytics**: implement fatigue math + readiness bands + deload triggers derived from events.

These units are scaffolded under `spec/006+` so each step is independently verifiable.
