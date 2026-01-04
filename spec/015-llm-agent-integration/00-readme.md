# 015 — LLM Agent Integration

## Goal

Make the `agent` service capable of generating coach responses via a real LLM provider, while keeping a safe stub fallback for local dev.

## Acceptance criteria

- Agent `POST /respond` supports an LLM-backed mode controlled by environment variables.
- When LLM configuration is missing/invalid, the agent falls back to a deterministic stub response (no crash).
- API WebSocket chat can be configured to call the agent (`CHAT_BACKEND=http`).
- No A2UI actions required in this unit.

## Non-goals

- Plan generation logic (handled by spec unit 008).
- Tool calling / A2UI.
- Auth and multi-user.
