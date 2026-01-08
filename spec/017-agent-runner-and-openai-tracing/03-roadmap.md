# Roadmap (Pre‑MVP)

## Milestone 1 — Agent is runner, UI still works
- API WS becomes a relay.
- Agent service owns the run/tool loop.
- Tools are called via API endpoints.

## Milestone 2 — OpenAI dashboard tracing is visible
- Runs appear in OpenAI dashboard.
- Traces are searchable by `threadId`/`runId`/user.

## Milestone 3 — Profile collection tooling
- Primary test goal: validate stack by filling out user profile via tool calls.
- The agent should:
  - detect missing profile fields
  - ask for them
  - call profile update tools
  - confirm saved state

## Deferred
- Username/password auth beyond “safe storage/transport”.
- Recovery flows.
- Rate limiting.
- Multi-user admin.
- Advanced observability correlation across OpenAI tracing and OTEL traces.
