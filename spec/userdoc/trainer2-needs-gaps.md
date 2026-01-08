# trainer2 — Project Summary, Needs, and Gaps (Jan 2026)

## What trainer2 is today

trainer2 is a docker-compose “walking skeleton” for an LLM-powered coaching app with a clean separation of concerns:

- **Web (Next.js)**: the user-facing chat UI.
- **API (FastAPI)**: authentication, WebSocket gateway (`WS /realtime`), persistence (Postgres), and the *trusted* executor for side effects.
- **Agent (FastAPI + OpenAI Agents SDK)**: runs the coach agent via `POST /run` and streams events (NDJSON) back to the API.

The runtime message path is:
- Browser ↔ API over WebSocket (`/realtime`)
- API → Agent over HTTP (`POST /run`, streaming)
- Agent → API for side effects via internal tool execution (`POST /internal/tools/execute`)

The system already supports a capabilities pipeline:
- API publishes **tools + table cards** at `GET /capabilities` (agent-authenticated)
- Agent caches those into `services/agent/app/generated/` (tools JSON + table_cards markdown)
- Agent prompt compilation currently includes the tool index + (currently) all table cards

## What you want (product direction)

You want to move from “one hardcoded onboarding profile” to a scalable pattern:

1) **CRUD-first domains** (starting with weights):
   - The coach can create/list/update/delete weight entries through tools.
   - The user can pull up a fully editable form, edit rows, and save.

2) **Modularity** (multiple agents + multiple skills):
   - Add new tables/forms fast without editing many files.
   - Add new agents/personas without reworking the entire prompt/tooling surface.

3) **On-demand context** (no “load everything every run”):
   - The agent should fetch domain-specific “skill docs” (table cards, schemas, form specs) only when needed.
   - Capabilities should be auditable and versioned.

4) **Strict UI contract (A2UI)** without requiring a full renderer:
   - Emit a structured UI tree that the frontend can render.
   - Keep the subset small (batch editor + Save).
   - Keep side effects server-side.

5) **Human-in-the-loop audit mode** (`/coach_audit`):
   - See the full context at each step.
   - Approve/deny/edit tool calls and optionally the final assistant response.
   - Auto-approve safe reads; require approval for risky writes.

## What’s working well

- The trust boundary is correct: **API executes side effects**, not the agent or browser.
- Streaming is in place and debuggable: you can observe tool start/result events.
- Capabilities → generated artifacts are auditable and provide a path to modular “skills”.

## Current gaps (the “wheel you’re reinventing”)

### 1) Capability loading is not modular yet
- Today, the compiled prompt includes *all* table cards.
- You want: base persona stays stable, and domain “skill docs” are fetched on demand.

### 2) CRUD/tool wiring scales poorly
- Tools are defined in multiple places:
  - tool schemas (OpenAI tool JSON)
  - tool execution dispatch in the API
  - table card registry/docs
- You want: one registry entry per domain/table that can generate:
  - tool schemas (preferably from Pydantic)
  - tool dispatch registration (avoid long if/elif ladders)
  - table card markdown

### 3) Forms need a minimal renderer loop
- The weights feature requires at least:
  - a “batch editor” UI (rows, add/delete, Save)
  - an action protocol (Save triggers one batch tool call)
- You do not need a full A2UI renderer, but you do need a small subset + wiring.

### 4) Safe bulk editing needs first-class support
- If forms generate many edits, doing `*_update` per row is token- and latency-expensive.
- You want a standard “forms-friendly” tool shape like `*_save_batch`.

### 5) Audit mode needs a first-class state machine
- The existing streaming loop is informative, but it’s not controllable.
- You want a controllable run coordinator:
  - stage context (optional)
  - gate tool calls
  - optionally gate the final response
  - auto-approve policy

## Key design constraints (to keep future tables fast)

- **One extension point per new table** (ideally): add a migration + one registry entry.
- **One stable base persona**: avoid editing `coach.md` per table; capabilities should teach “what exists”.
- **One safe UI loop**: no frontend-side privileged actions; UI emits intents, backend executes.
- **Auditability**: log which capability version/hash was used for each run.

## Near-term “smallest next steps” (sequence)

1) Weights domain: add table + CRUD tools + a batch-save tool.
2) Minimal batch editor UI (not full A2UI): render rows + Save triggers one batch call.
3) Generate tool schemas from Pydantic args models (stop hand-writing tool JSON).
4) Replace tool dispatch if/elif ladder with a registry/router.
5) Add `/coach_audit` route to gate tool calls (human approval) as you iterate.
