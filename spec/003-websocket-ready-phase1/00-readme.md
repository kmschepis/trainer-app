# 003 — WebSocket Ready for Phase 1

## Goal

Upgrade the Phase 0 websocket from raw echo to a **JSON message envelope** that supports:

- chat messages (client → API → agent → API → client)
- A2UI actions (agent → API → client)
- lightweight session IDs (no per-message “agent start/stop” overhead)

## Acceptance criteria

- WebSocket endpoint remains `ws://localhost:8000/realtime`.
- Client can send `{"type":"chat.send","message":"..."}` and receive:
  - `session.created` (if no sessionId provided)
  - `chat.message` response (assistant text)
- Agent service remains a long-running container; API calls it over HTTP (no subprocess-per-message).
- Web UI provides a minimal chat input and renders assistant replies.

## Notes

- This is not the full Phase 1 event model; it’s the realtime transport groundwork.
