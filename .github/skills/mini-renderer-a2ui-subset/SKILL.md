---
name: mini-renderer-a2ui-subset
description: Add a minimal A2UI-style renderer loop (render events + user actions) on top of the existing /run streaming architecture, without enabling UI side-effect tools.
---

## Mission

Enable a small, understandable “render loop”:
- Agent streams either text or a structured UI description.
- Web renders a tiny component subset.
- User interactions send structured actions back.
- API calls the agent again with that action.

Constraints:
- Keep transport unchanged (Browser WS `/realtime` → API → Agent `POST /run`).
- No browser automation / side-effect UI tools.
- Start with a tiny component set.

## When to use (triggers)

- You want “forms/buttons” in the chat UI.
- You want deterministic, inspectable UI outputs.
- You want to iterate on UI behavior without adding a full renderer framework.

## Inputs

- Agent streaming endpoint: `services/agent/app/main.py` (`POST /run`)
- Agent runner: `services/agent/app/runner.py`
- API realtime WS: `services/api/app/routes/realtime.py`
- Web chat client: `apps/web/app/coach/useCoachChat.ts`
- Coach prompt: `services/agent/app/instructions/agents/coach.md`

## Outputs

- A new streamed event type forwarded to the browser:
  - `a2ui.render` with `{ view, state, version }`
- A new WS inbound message type from browser:
  - `a2ui.action` with `{ action, args, viewVersion }`
- A small React renderer mapping node types to components.

## Suggested “mini” component set

- `Column`
- `Row`
- `Text`
- `Button`
- `Input`

## Prompt contract (recommended)

- If UI is helpful, emit exactly one fenced code block:
  - language: `a2ui`
  - content: JSON object
- If not, respond normally with text.
- When receiving an action, treat it as the next user turn and update the UI.

Example convention:
- User action message prefix: `A2UI_ACTION:` followed by JSON.

## Workflow

1. Web sends `chat.send` as today.
2. API calls agent `POST /run` and forwards streamed NDJSON events.
3. Agent emits either:
   - normal text chunks, OR
   - an `a2ui.render` event (parsed from a ```a2ui fenced block).
4. Web renderer updates the “UI panel” state from `a2ui.render`.
5. On click/input, web sends `a2ui.action` over WS.
6. API turns that into a new agent `/run` call (same session) and forwards the response.

## Verify

- Sending a chat yields either text or a rendered UI.
- Clicking a button sends `a2ui.action` and triggers a new `/run`.
- All payloads are visible in WS frames and agent stream logs.
