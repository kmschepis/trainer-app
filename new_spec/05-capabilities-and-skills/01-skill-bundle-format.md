# Skill bundle format

A skill bundle is the unit of “on-demand context” for the agent.

## Goals

- Operator-editable.
- Strictly scoped: only what’s needed for the capability.
- Includes examples that map to real tool calls and A2UI.

## Suggested structure

A single bundle per capability version:

- `capability.json`
- `tools.json`
- `ui_schemas.json`
- `skill.md`

## `skill.md` template

```md
---
capability_id: weights
version: 1
intent_triggers:
  - weigh-in
  - bodyweight
---

# Weights skill

## When to use

Use when the user logs, imports, or reviews weigh-ins.

## Default behavior

- Unit: lbs
- List: last 30 entries
- Date-only becomes noon local

## Tools

- weight_entry_list
- weight_entry_save_batch
- weight_entry_delete_batch

## UI

- Render `WeightEntryForm.v1` for confirmation
- Render `WeightBatchEditor.v1` for imports

## Examples

### Single entry

User: Weigh-in 187.6 today

1) Render form with measured_at prefilled
2) On submit, call weight_entry_save_batch

### Import

User pastes table...

1) Parse
2) Ask one clarifying question if needed
3) Render batch editor
4) On save, call weight_entry_save_batch
```

## Loading

The agent asks the registry for a bundle by `capability_id` and version.
The UI can also load UI schemas by capability version.
