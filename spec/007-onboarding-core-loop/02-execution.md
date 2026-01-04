# 007 — Execution Log

- Implemented a chat-first onboarding UX using A2UI-style actions.
- Web UI now includes a slide-over onboarding form that can be opened/updated/closed via `a2ui.action` messages.
- Refactored the web chat UI into small components under `apps/web/app/components/`.
- Moved the agent system prompt into a file (`services/agent/app/prompts/system.txt`) with env override support.
