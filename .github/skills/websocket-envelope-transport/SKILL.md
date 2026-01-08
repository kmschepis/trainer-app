---
name: websocket-envelope-transport
description: Implement or maintain the JSON-envelope WebSocket protocol for realtime chat between web ↔ api and api ↔ agent. Use when making the app “Phase 1 ready” without adding per-message overhead.
---

## Mission

Keep a stable, debuggable realtime transport with:
- predictable message shapes
- session correlation (`sessionId`)
- request correlation (`requestId`)
- backwards-compatible handling for non-JSON clients

## When to use (triggers)

- Updating WS message types or adding new realtime events.
- Fixing chat send/receive issues in the web UI.
- Ensuring API forwards to the agent service correctly.

## Inputs

- API WS endpoint in `services/api/app/main.py`
- Agent endpoint `POST /run` in `services/agent/app/main.py`
- Web client in `apps/web/app/page.tsx`

## Outputs

- WebSocket endpoint `WS /realtime` supporting:
  - `ping` → `pong`
  - `session.created`
  - `chat.send` → calls agent → emits `chat.message`
  - `a2ui.action` relay
- Session defaults: API generates `sessionId` if missing.

## Protocol notes

Envelope (typical):
- `type`: string message type
- `sessionId`: string
- `requestId`: optional string for correlation
- `payload`: object (shape depends on `type`)

Fallback:
- If client sends raw text / non-JSON, API may echo or return an error envelope.

## Workflow

1. Web client sends:
   - `ping` immediately on connect.
   - `chat.send` with user message.
2. API:
   - ensures/creates `sessionId` and emits `session.created`.
   - calls agent over internal HTTP (`AGENT_BASE_URL`).
   - sends `chat.message` with agent response.
   - forwards any `a2uiActions` as `a2ui.action` messages.
3. Agent:
   - returns `{ text, a2uiActions }`.

## Verify

- In browser, send a message and confirm:
  - WS stays open
  - you receive `chat.message`
  - any UI actions render as JSON in the page

## Example (from this repo)

- WS handler: `services/api/app/main.py`
- Agent responder: `services/agent/app/main.py`
- Web chat UI: `apps/web/app/page.tsx`
