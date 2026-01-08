# Tool contract (conceptual)

Tools are how the agent asks the system to do things.

## Principles

- Tools are executed by the API Executor (not the agent).
- Tools are versioned via capability versions.
- Write tools are gated (see audit spec).

## Tool schema

A tool is defined by:
- `name`
- `description`
- `args_schema` (JSON Schema or equivalent)
- `result_schema`
- `policy` (read/write, approval requirements)

Minimal conceptual representation:

```json
{
  "name": "weight_entry_save_batch",
  "description": "Create/update weight entries in a single batch.",
  "args_schema": {
    "type": "object",
    "properties": {
      "rows": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": ["string", "null"]},
            "measured_at": {"type": "string", "format": "date-time"},
            "weight_lbs": {"type": "number"},
            "notes": {"type": "string"}
          },
          "required": ["measured_at", "weight_lbs"]
        }
      }
    },
    "required": ["rows"]
  },
  "result_schema": {
    "type": "object",
    "properties": {
      "saved": {"type": "integer"},
      "ids": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["saved", "ids"]
  },
  "policy": {
    "kind": "write",
    "requires_approval": true
  }
}
```

## Batch-first UX

We prefer `*_save_batch` tools because:
- UI editing is interactive and would otherwise cause too many tool calls.
- Validation can happen client-side, then server-side.

## Idempotency

Write tools support one of:
- deterministic `id` provided by client, or
- `idempotency_key` at request level.

The platform should guarantee: repeated identical calls do not duplicate writes.

## Errors

Error payloads must be:
- structured (`code`, `message`, `details`)
- safe to show to end users (no stack traces)
