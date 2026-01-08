# Plan — Agent Runner Rebuild + OpenAI Dashboard Tracing

## 1) Define contracts first (no implementation yet)

### 1.1 Event stream contract (Agent → API → Browser)
We want a minimal set of event types that the UI can render, and that can be persisted.

**Required event types** (existing names are fine; keep them stable):
- `RUN_STARTED` — includes `threadId`, `runId`, optional `parentRunId`.
- `TOOL_CALL_STARTED` — includes `runId`, `toolName`, optional `label`.
- `TOOL_CALL_RESULT` — includes `runId`, `toolName`, optional `label`, optional `ok`/`error`.
- `TEXT_MESSAGE_CHUNK` — includes `runId`, `delta`.
- `RUN_ERROR` — includes `runId`, `message`.
- `RUN_FINISHED` — includes `runId`.

**Notes**
- Keep the event payload JSON-only.
- Ensure every event carries `threadId` and `runId` once the run starts.

### 1.2 “Run request” contract (API → Agent)
When the browser sends a message over WS, the API will forward a *run request* to the agent.

Minimal payload:
- `threadId`: string
- `user`: { `id`: string } (or `userId`: string)
- `message`: string (user text)
- `contextRef`: optional pointer (or embed a snapshot; decision below)

Decision point: **context embedding vs context fetch**
- Option A (preferred): agent fetches state via tool endpoints (`GET /state?threadId=...`).
- Option B: API sends snapshot inline (risk: drift + larger payloads).

### 1.3 Tool backend contract (Agent → API)
Expose explicit tool endpoints that the agent calls.

Each tool endpoint:
- Authenticates as an internal caller.
- Is scoped to a specific user + thread.
- Validates input strictly.
- Writes to DB/event log.
- Returns a structured result.

Example categories:
- State read: `GET /state?threadId=...`
- Profile update: `POST /tools/profile.patch`
- Event append: `POST /events`

(Exact endpoints depend on the existing API tool system, but the contract should be “HTTP tools that are safe and validated”.)

## 2) Decide agent runner runtime + tracing model

### 2.1 Runner framework
Use the same “agents runner” approach as the legacy `.dev` implementation:
- `.dev/app/api/chat.py` uses `agents.Runner.run(...)` with `SQLiteSession`.

For this repo, we want:
- a session/thread concept keyed by `threadId` (already used by UI)
- stable run IDs
- instrumentation hooks for OpenAI tracing

### 2.2 OpenAI dashboard tracing
To see traces in OpenAI dashboard, we need:
- Agent service to call OpenAI through the SDK path that emits OpenAI traces.
- Agent service to be the place where the run loop happens.

We will verify:
- The agent container uses the correct API key/project.
- The agent container is not pointing at a non-OpenAI base URL when expecting OpenAI dashboard traces.

## 3) Authentication boundary (pre‑MVP)

Constraints:
- Browser auth stays at API.
- Agent must be able to call tools on behalf of a user/thread.
- Avoid giving agent direct DB credentials.

Proposed approach:
- API issues a short-lived “act-as” token scoped to:
  - `userId`
  - `threadId`
  - allowed tool endpoints
- Agent presents that token when calling API tool endpoints.

This avoids:
- Browser talking to agent directly
- Agent needing to validate Google tokens

## 4) Big-bang cutover steps (no flags)

1. Move runner loop responsibility to agent service.
2. Replace API websocket handler loop with a relay:
   - receive user message
   - persist it
   - forward run request to agent
   - forward agent events to browser
   - persist events
3. Ensure tools are reachable to agent through API endpoints.
4. Validate:
   - UI streaming works
   - DB state changes happen
   - OpenAI dashboard shows traces

## 5) Passwords / auth stance for pre‑MVP

You want “safe storage + safe transport” but you do not care about:
- recovery
- rate limiting

So for username/password auth (if implemented):
- Store password hashes with a modern salted KDF (argon2id / bcrypt).
- Transport only over HTTPS.
- Use httpOnly cookies for sessions.

Optional simplifying choice:
- Use Google OAuth only for now.

## Open Questions (should be answered before implementation)
- Do we want agent↔API streaming to be HTTP streaming (SSE) or WS?
- Should agent fetch state from API on-demand (preferred) or receive snapshot inline?
- What exact OpenAI dashboard tracing feature is desired (Agents SDK tracing vs Responses tracing) and which package/version corresponds to `.dev`’s `agents` import?
