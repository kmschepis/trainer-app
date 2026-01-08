# Execution Notes — Big Bang Rebuild (No Flags)

This document is intended to be followed during implementation.

## Phase 0 — Confirm current primitives
- Confirm current WS event names used by the UI.
- Confirm the API tool surface and how tools are executed today.
- Confirm what the `.dev` `agents` package is and how it enables OpenAI tracing.

## Phase 1 — Define the new message flows

### Flow A: user message → agent run
1. Browser sends a user message over WS to API.
2. API authenticates browser user.
3. API persists the user message.
4. API forwards a run request to agent (internal).
5. Agent starts a run and begins emitting events.
6. API relays events to browser and persists them.
7. Agent calls tools on API as needed.
8. Agent completes, sends RUN_FINISHED.

### Flow B: agent tool call
1. Agent decides to call a tool.
2. Agent calls API tool endpoint with scoped token.
3. API validates token scope + payload.
4. API writes state/events.
5. API returns tool result.
6. Agent emits TOOL_CALL_RESULT and continues run.

## Phase 2 — Implementation sequencing (recommended order)
1. Implement the tool backend contract (API endpoints the agent will call).
2. Implement the agent runner loop (using the Agents SDK runner).
3. Implement agent→API event streaming channel.
4. Modify API WS handler to relay (remove the local tool loop).

## Phase 3 — Validation checklist

### Functional
- From UI, send “hello”.
- See RUN_STARTED / TEXT_MESSAGE_CHUNK / RUN_FINISHED.
- Confirm persisted events exist for the user/thread.
- Confirm profile update tool calls round-trip correctly.

### Tracing
- Confirm OpenAI dashboard shows:
  - at least one trace per run
  - model inputs/outputs visible enough to debug
  - tool call steps visible (if supported)

### Failure mode
- If a tool endpoint returns 4xx, agent emits RUN_ERROR and stops.
- If OpenAI call fails, agent emits RUN_ERROR and stops.

## Phase 4 — Cleanup
- Remove now-obsolete logic from API that previously orchestrated tool loops.
- Ensure the agent service is the only place making OpenAI calls.
