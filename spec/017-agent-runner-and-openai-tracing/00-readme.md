# 017 — Agent Runner Rebuild + OpenAI Dashboard Tracing

## Goal
Make the **agent service** the true *agent runner* (planning + tool loop + streaming), and make the **API** the *authenticated gateway + tools/data backend*.

This change is specifically motivated by:
- Getting **full OpenAI dashboard tracing** for runs (model calls + tool decisions + step lifecycle).
- Removing the “API orchestrates the agent loop” coupling.
- Keeping the browser websocket/auth boundary at the API.

Non-goals (explicitly out of scope for this pre‑MVP phase):
- Account recovery flows (email verification, password reset, etc.).
- Rate limiting / production hardening.
- Multi-user admin tooling.

## Current State (as implemented today)
- Browser connects to API over WebSocket (`/realtime`).
- API runs the multi-step loop: calls agent for a model step, executes tools, persists events/state, streams events to browser.
- Agent service is primarily the streaming runner via `POST /run` (NDJSON events).

Consequence: the agent service is not a cohesive runner, and OpenAI dashboard tracing will not show a coherent multi-step run unless the runner logic lives where the model calls live.

## Target State (desired architecture)
### Responsibilities
- Web:
  - UI only.
  - Auth flow (Google OAuth today via NextAuth).
  - Chat UI with streaming events.

- API (gateway + tools + persistence):
  - Owns **browser-facing auth**.
  - Owns **WebSocket connection**.
  - Persists **user message** and **run events**.
  - Provides **tool endpoints** (validated DB/state updates).
  - Does **not** decide “what to do next” in the run.

- Agent (runner + OpenAI tracing):
  - Owns the **run loop** (plan → decide → call tool(s) → incorporate results → respond).
  - Calls OpenAI (or compatible base URL) and ensures **OpenAI dashboard tracing is enabled**.
  - Calls API tool endpoints to read/write state.
  - Streams run lifecycle events back (via API relay).

### Connectivity
- Browser ⇄ API: WebSocket (existing).
- API ⇄ Agent: internal (HTTP or WebSocket; choose one; see Plan).
- Agent ⇄ API: HTTP tool calls.
- Agent ⇄ OpenAI: HTTPS.

## Key Design Choice
Keep **Browser ⇄ API WS** (API remains the auth gateway).

Rationale:
- Keeps the agent off the public edge.
- Avoids duplicating auth logic in the agent.
- Avoids making the agent service responsible for rate limiting / abuse handling.

## What must be true when we are “done”
- The API no longer contains the “tool calling loop” logic.
- The agent service owns the runner loop.
- The web UI still speaks to a single WS endpoint at the API.
- OpenAI dashboard shows traces for agent runs.

## Deliverables
- A stable event protocol for streaming run lifecycle and tool progress.
- A tool endpoint interface on API that the agent can call.
- A secure(ish) pre‑MVP auth boundary:
  - browser authenticates to API
  - agent uses scoped internal authorization to act on behalf of a user/thread

## Acceptance Criteria
- A single chat message produces:
  - streaming events in the UI (RUN_STARTED → tool events → text chunks → RUN_FINISHED)
  - persisted events/state in DB
  - a visible run trace in OpenAI dashboard

## Files / References
- Current agent runtime path: services/agent/app/runner.py (Agents SDK)
- Current API WS orchestration: services/api/app/routes/realtime.py
- Legacy runner example: .dev/app/api/chat.py (uses `agents.Runner`)
