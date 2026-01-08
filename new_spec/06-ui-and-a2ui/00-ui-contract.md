# UI contract (A2UI)

A2UI is a strict, machine-readable UI schema the agent can output and the frontend can render.

## Principles

- The agent emits **data**, not React.
- The UI renderer is deterministic.
- User actions are emitted back as typed events.

## Envelope

The agent outputs:
- optional text (`assistant.message`)
- optional view tree (`assistant.view`)

The view tree is:

```json
{
  "kind": "a2ui.v1",
  "view_id": "view_...",
  "title": "Confirm weigh-in",
  "tree": {}
}
```

## Minimum component subset (v1)

This spec intentionally keeps the set small.

- `screen`
- `section`
- `text`
- `form`
- `field.text`
- `field.number`
- `field.datetime`
- `table_editor`
- `button`

## Form contract

A form node:

```json
{
  "type": "form",
  "id": "weight_entry",
  "fields": [
    {"type": "field.datetime", "name": "measured_at", "label": "Measured at", "required": true},
    {"type": "field.number", "name": "weight_lbs", "label": "Weight (lbs)", "required": true},
    {"type": "field.text", "name": "notes", "label": "Notes", "required": false}
  ],
  "submit": {"label": "Save"}
}
```

On submit, the UI emits `ui.action` with `kind: form.submit` and `values`.

## Batch editor contract

A batch editor is a grid of rows with per-cell editing.

```json
{
  "type": "table_editor",
  "id": "weight_batch",
  "columns": [
    {"key": "measured_at", "label": "Measured at", "type": "datetime", "required": true},
    {"key": "weight_lbs", "label": "Weight (lbs)", "type": "number", "required": true},
    {"key": "notes", "label": "Notes", "type": "text"}
  ],
  "rows": [
    {"row_id": "r1", "measured_at": "2026-01-08T12:00:00-05:00", "weight_lbs": 187.6, "notes": ""}
  ],
  "actions": [
    {"kind": "table.save", "label": "Save all"},
    {"kind": "table.add_row", "label": "Add row"}
  ]
}
```

User actions:
- `table.save` with current rows
- `table.add_row`
- `table.delete_row`

## Validation

- Client validates required fields and simple types.
- Server validates again and returns structured errors.
- The UI can map `error.details.path` to a field/cell.
