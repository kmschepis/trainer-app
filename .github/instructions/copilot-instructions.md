
# Copilot instructions (trainer2)

## Big picture

- Stack is container-first: **Next.js web** + **FastAPI API** + **FastAPI agent placeholder** + **Postgres**, orchestrated by `compose.yml`.
- Phase 0 goal is a walking skeleton (boot + `/health` + WebSocket echo). Avoid adding extra features outside the active spec unit.

## Repo layout

- `apps/web/` — Next.js app (Phase 0 page connects to API WS).
- `services/api/` — FastAPI app (`GET /health`, `WS /realtime`).
- `services/agent/` — placeholder service that just boots (`GET /health`).
- `spec/` — **Markdown-only specs** and numbered work units.

## Local dev (authoritative)

- Start: `docker compose up --build -d`
- Status: `docker compose ps`
- Stop: `docker compose down`
- Web: `http://localhost:3000`
- API: `http://localhost:8000/health`
- Agent: `http://localhost:9000/health`

## Spec-driven workflow (must follow)

The `spec/` folder is the source of truth for work.

- Each work unit lives in `spec/NNN-short-name/` (strict: no spaces).
- Each folder (including `spec/`) must contain a `00-readme.md`.
- Each unit folder must contain:
	- `00-readme.md`: user story + acceptance criteria (A/C)
	- `01-plan.md`: detailed plan
	- `02-execution.md`: running log of actual work performed

When you change code:

- Identify the active unit folder and update its `02-execution.md` in the same session.
- Keep `00-readme.md` acceptance criteria accurate.
- If work doesn’t fit an existing unit, create a new numbered unit folder and start `00/01/02`.

## Conventions

- Keep Phase 0 minimal: no auth, migrations, or event schema unless the active unit requires it.
- Prefer API-owned realtime via WebSocket (`/realtime`), with the web client connecting to the API.

## Autonomy (decision making)

- Default to **sensible, strict conventions** without asking (e.g., `spec/NNN-kebab-case/`, no spaces).
- Do not ask the user low-value preference questions (formatting, naming, minor tooling choices). Just pick the simplest option that fits the current spec unit.
- Ask a question only when the decision:
	- materially changes product behavior or UX,
	- risks significant rework,
	- affects security/privacy boundaries,
	- or is genuinely blocked by missing information.
- If multiple options are viable, choose one and proceed; record the choice in the active unit’s `02-execution.md`.

