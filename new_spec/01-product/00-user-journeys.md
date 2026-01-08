# User journeys

These are the minimum journeys the platform must support.

## Journey A — Quick log (weights)

1) User: “Weigh-in 187.6 today”
2) Coach: confirms interpretation (timezone/year only if ambiguous)
3) Coach: shows a compact editable form (A2UI)
4) User: hits Save
5) System: writes to DB (with approval gate depending on mode)
6) Coach: acknowledges + shows last 30 entries

Success criteria:
- User can correct date/time/unit before saving.
- The system never writes without an explicit tool call.

## Journey B — Import from pasted table

1) User pastes a Markdown-ish table of weigh-ins
2) Coach asks a single clarifying question if needed (year + timezone)
3) Coach renders a batch editor UI with parsed rows
4) User reviews/edits/deletes rows
5) User hits Save All
6) System writes via `weight_entry_save_batch`

Success criteria:
- Import is deterministic (no “silent” guessing).
- User sees exactly what will be saved.

## Journey C — Program execution (workout day)

1) User: “Today is squat day”
2) Coach loads the relevant skill on-demand (workouts)
3) Coach presents a structured workout canvas
4) User logs sets/reps/weight
5) Coach persists sets in batches and summarizes session

Success criteria:
- UI is responsive; tool calls are coarse (batch).

## Journey D — Operator adds a new capability

1) Operator opens Studio
2) Defines:
   - a table schema (fields + validation)
   - a default form (A2UI)
   - tool permissions (read vs write)
   - one or more agent “skills” (instructions + examples)
3) Publishes version `v1`
4) The new capability appears in the registry; the agent can load it on-demand

Success criteria:
- No code deploy is needed for the first useful version.
- Audit policies apply automatically.

## Modes

- **Normal mode**: reads are auto-approved; writes require explicit user confirmation.
- **Audit mode**: a human operator approves writes (and optionally response/context) in an audit console.
