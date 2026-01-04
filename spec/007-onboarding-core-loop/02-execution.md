# 007 — Execution Log

- Implemented a chat-first onboarding UX using A2UI-style actions.
- Web UI now includes a slide-over onboarding form that can be opened/updated/closed via `a2ui.action` messages.
- Refactored the web chat UI into small components under `apps/web/app/components/`.
- Moved the agent system prompt into a file (`services/agent/app/prompts/system.txt`) with env override support.
- Added an architecture decision memo for how the agent should act (domain tools executed by the API; events remain the ledger): `agent-paradigm.md`.
- Canonicalized the profile persistence event name to `ProfileSaved` (with backward-compat for `UserOnboarded`) and added `ProfileDeleted` support in the state projector.
- Added a minimal API tool execution service (`profile.save`/`profile.delete`) and wired it into the websocket flow with `TOOL_CALL_*` AG-UI events.
- Updated the API chat handler to open onboarding when `hasProfile` is false and to treat `ONBOARDING_SUBMIT` as a `profile.save` tool call.
- Updated the web client to set `hasProfile=true` when the server sends `ui.onboarding.close`.
