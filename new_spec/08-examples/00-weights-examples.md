# Examples — weights

## Example 1: single weigh-in

User: “Weigh-in 187.6 today”

Agent:
1) Emits a confirmation form (A2UI)
2) User submits
3) Calls `weight_entry_save_batch`

A2UI (sketch):

```json
{
  "kind": "a2ui.v1",
  "view_id": "view_confirm_weight",
  "title": "Confirm weigh-in",
  "tree": {
    "type": "screen",
    "children": [
      {"type": "text", "text": "Please confirm this weigh-in."},
      {
        "type": "form",
        "id": "weight_entry",
        "fields": [
          {"type": "field.datetime", "name": "measured_at", "label": "Measured at", "required": true},
          {"type": "field.number", "name": "weight_lbs", "label": "Weight (lbs)", "required": true},
          {"type": "field.text", "name": "notes", "label": "Notes"}
        ],
        "submit": {"label": "Save"}
      }
    ]
  }
}
```

Tool call args:

```json
{
  "rows": [
    {
      "measured_at": "2026-01-08T12:00:00-05:00",
      "weight_lbs": 187.6,
      "notes": ""
    }
  ]
}
```

## Example 2: import from pasted table

User:

```text
| date | weight |
|------|--------|
| 01/02 | 190.2 |
| 01/05 | 189.6 |
```

Agent:
1) Asks: “What year and timezone should I assume for these dates?”
2) Renders batch editor with parsed rows
3) User edits a row and saves
4) Agent calls `weight_entry_save_batch`
