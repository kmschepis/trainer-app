# Spec Workflow (Authoritative)

This repository uses **spec-driven development**.

## Folder rules

- `spec/` contains **only Markdown files** and **numbered unit folders**.
- Each unit of work lives in a numbered folder: `spec/NNN-kebab-case/` (**strict: no spaces**).
- Every folder (including `spec/` itself) must contain a `00-readme.md`.

## Per-unit document set

Inside each unit folder:

- `00-readme.md` — the user story + context + acceptance criteria (A/C). This is the authoritative statement of “what done means”.
- `01-plan.md` — detailed, step-by-step plan to accomplish the unit.
- `02-execution.md` — a running log of work performed (decisions, commands run, files changed, verification notes).

## Agent rule (non-negotiable)

When AI agents make changes for a unit:

- Update that unit’s `02-execution.md` in the same session.
- Keep the `00-readme.md` acceptance criteria accurate (don’t let it drift).
- If work does not fit an existing unit, create a new numbered unit folder and start the `00/01/02` files.

## Current units

- `spec/001-init/` — initial product/architecture spec
- `spec/002-phase0-walking-skeleton/` — Docker Compose + boot checks
- `spec/003-websocket-ready-phase1/` — WS envelope + API→agent chat transport
- `spec/004-observability-stack/` — metrics/logs/traces + Grafana
- `spec/005-template-hardening/` — additional skeleton work to make this a reusable agentic-project template
- `spec/006-event-log-and-state-view/` — append-only events + `GET /state` materialization
- `spec/007-onboarding-core-loop/` — onboarding form → events → state
- `spec/008-agent-plan-generation/` — 1-week plan markdown generation + persistence
- `spec/009-workout-canvas-and-set-logging/` — workout view + set logging events
- `spec/010-weekly-review/` — weekly review page and basic derived metrics
- `spec/011-plan-diff-proposals/` — plan diff propose/accept/deny (no silent edits)
- `spec/012-fatigue-analytics/` — fatigue math + readiness bands derived from events
