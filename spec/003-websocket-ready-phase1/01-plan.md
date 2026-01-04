# 003 — Plan

1. Define WS envelope shapes:
   - `ping`/`pong`
   - `chat.send` → `chat.message`
   - `a2ui.action`
   - `error`
2. Update API websocket handler to:
   - accept JSON messages
   - create/return a `sessionId` when missing
   - call agent over HTTP for `chat.send`
3. Update agent service to expose `POST /respond` returning `{text, a2uiActions[]}`.
4. Update web to:
   - connect to WS
   - send `chat.send`
   - display responses and actions
5. Verify via `docker compose up --build -d` and manual UI check.
