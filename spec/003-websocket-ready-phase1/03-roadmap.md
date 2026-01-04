# 003 — Work Items Roadmap

Status: complete (see `02-execution.md`).

## Work items

- [x] Define and implement WS JSON envelope types (ping/pong, chat, a2ui, error).
- [x] API generates/returns `sessionId` when missing.
- [x] API forwards `chat.send` to agent over HTTP.
- [x] Agent implements `POST /respond` returning `{text, a2uiActions[]}`.
- [x] Web provides a minimal chat UI and renders replies.

## Notes

- This is transport groundwork; not the full Phase 1 event model.
