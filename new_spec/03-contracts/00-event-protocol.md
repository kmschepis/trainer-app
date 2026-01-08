# Event protocol (conceptual)

This document defines the *shapes* of messages that move between Web UI, Agent, and API Executor.

## Design goals

- Explicit, typed envelopes (easy to log, replay, audit).
- Correlation IDs everywhere.
- UI events are distinct from tool calls.

## Common envelope

All events use:

```json
{
  "type": "string",
  "id": "evt_...",
  "ts": "2026-01-08T12:34:56.789Z",
  "trace_id": "tr_...",
  "session_id": "sess_...",
  "payload": {}
}
```

## UI → Agent: user input

### `ui.message`

```json
{
  "type": "ui.message",
  "id": "evt_...",
  "ts": "...",
  "session_id": "...",
  "payload": {
    "text": "Weigh-in 187.6 today"
  }
}
```

### `ui.action`

User interacted with rendered A2UI.

```json
{
  "type": "ui.action",
  "id": "evt_...",
  "ts": "...",
  "session_id": "...",
  "payload": {
    "view_id": "view_...",
    "action": {
      "kind": "form.submit",
      "form_id": "weight_entry",
      "values": {
        "measured_at": "2026-01-08",
        "weight_lbs": 187.6
      }
    }
  }
}
```

## Agent → UI: assistant output

### `assistant.message`

```json
{
  "type": "assistant.message",
  "id": "evt_...",
  "ts": "...",
  "session_id": "...",
  "payload": {
    "text": "Got it. Please confirm the entry:"
  }
}
```

### `assistant.view`

```json
{
  "type": "assistant.view",
  "id": "evt_...",
  "ts": "...",
  "session_id": "...",
  "payload": {
    "view": {
      "kind": "a2ui.v1",
      "view_id": "view_...",
      "tree": {}
    }
  }
}
```

## Agent → API Executor: tool call request

Tools are requested by name with JSON args.

```json
{
  "type": "tool.call",
  "id": "evt_...",
  "ts": "...",
  "trace_id": "tr_...",
  "session_id": "...",
  "payload": {
    "tool": "weight_entry_save_batch",
    "args": {
      "rows": [
        {
          "measured_at": "2026-01-08T12:00:00-05:00",
          "weight_lbs": 187.6,
          "notes": ""
        }
      ]
    }
  }
}
```

## API Executor → Agent: tool result

```json
{
  "type": "tool.result",
  "id": "evt_...",
  "ts": "...",
  "trace_id": "tr_...",
  "session_id": "...",
  "payload": {
    "tool": "weight_entry_save_batch",
    "ok": true,
    "result": {
      "saved": 1,
      "ids": ["wt_..."]
    },
    "error": null
  }
}
```

Error case:

```json
{
  "type": "tool.result",
  "id": "evt_...",
  "ts": "...",
  "trace_id": "tr_...",
  "session_id": "...",
  "payload": {
    "tool": "weight_entry_save_batch",
    "ok": false,
    "result": null,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "weight_lbs must be > 0",
      "details": {"path": ["rows", 0, "weight_lbs"]}
    }
  }
}
```
