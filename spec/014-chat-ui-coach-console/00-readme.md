# 014 — Chat UI Coach Console

## Goal

Make the web app’s first user-facing experience a **nice-looking, chat-first coach console** for local iteration.

## Acceptance criteria

- Web renders a sleek, dark chat UI suitable for daily use.
- User can chat with the coach over the existing WebSocket protocol (`chat.send` → `chat.message`).
- No A2UI actions, side panes, or multi-panel context in this unit.
- Chat works without any LLM integration (built-in stub responses are acceptable).
- UI clearly shows basic connection state (connected / disconnected).

## Non-goals

- Onboarding form.
- Workout canvas, set logger, timers.
- Persisting chat messages as events.
