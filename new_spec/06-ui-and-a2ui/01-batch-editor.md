# Batch editor behavior

The batch editor is the critical UI for making writes safe and efficient.

## Requirements

- Edit many rows without triggering tool calls.
- Show validation errors inline.
- Allow row deletion before saving.

## Save semantics

- Clicking “Save all” emits one `ui.action` containing the full row set.
- The agent calls `*_save_batch` exactly once per save.

## Error mapping

When a save fails with structured errors, the UI must be able to highlight:
- a specific cell (row + column)
- or a row-level error

## Minimal UX

No advanced features in v1:
- no sorting
- no filtering
- no pagination

(Those are future concerns; keep v1 deterministic and small.)
