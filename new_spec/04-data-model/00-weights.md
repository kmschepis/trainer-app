# Data model — weights

This is the first “real” domain module and sets the pattern for others.

## Canonical decisions

- Canonical unit: **lbs**.
- Storage type: `NUMERIC(6,2)` (or equivalent) for weight.
- Default listing: **last 30** entries.
- If the user provides a date without time, interpret as **12:00 PM local time**.

## Entities

### `weight_entries`

Fields:
- `id` (string/uuid)
- `user_id`
- `measured_at` (timestamp with timezone)
- `weight_lbs` (numeric(6,2))
- `notes` (optional string)
- `created_at`, `updated_at`

Constraints:
- `weight_lbs > 0`
- Optional: uniqueness on (`user_id`, `measured_at`) to prevent duplicates

## Tools

### Read tools

- `weight_entry_list({ limit=30, cursor? })`
- `weight_entry_get({ id })`

### Write tools

- `weight_entry_save_batch({ rows: WeightEntryUpsert[] })`
- `weight_entry_delete_batch({ ids: string[] })`

Where `WeightEntryUpsert`:
- `id?` (if present: update; else: create)
- `measured_at`
- `weight_lbs`
- `notes?`

## Import parsing rules (for pasted tables)

- Accept rows with:
  - date only (`YYYY-MM-DD`) or
  - date-time, optionally with timezone
- If date-only rows exist:
  - ask 1 clarifying question if needed: “What year and timezone should I assume?”
  - convert date-only to `12:00 PM` in that timezone
- Normalize all weights to lbs.

## Default UI

- A “single entry” form (date/time, weight, notes).
- A batch editor grid for imports and multi-edit.

The UI contract for these is defined in [06-ui-and-a2ui/00-ui-contract.md](../06-ui-and-a2ui/00-ui-contract.md).
