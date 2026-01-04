# 009 — Workout Canvas + Set Logging

## Goal

Deliver the “today workout” experience:

- left pane: plan markdown
- right pane: interactive set logger
- logging emits `SetLogged` events

## Acceptance criteria

- Web renders the current plan markdown from `GET /state`.
- Web provides a set logger UI for the day’s session.
- Logging a set appends a `SetLogged` event.
- State projection includes logged sets for the current session/day.
- (Optional but MVP-aligned) Rest timer starts when a set is logged.

## Non-goals

- Full exercise library; minimal hard-coded exercises is acceptable for v1.
- Conditioning logging.
