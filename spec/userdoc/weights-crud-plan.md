# Weights Table + CRUD + Editable Form — Plan (trainer2)

You want:
- user logs weigh-ins by chatting with coach
- full CRUD (create/list/update/delete)
- user can open an editable form, change weigh-ins, save
- adding the *next* table should feel repeatable and low-touch

Constraints / decisions (from you):
- **no goal weight (for now)**
- canonical unit: **lbs**
- `measured_at` is **editable** (backdating allowed)
- `weight_entry_list` default: **last 30**
- date-only inputs: **assume 12:00 PM local time**
- `weight_lbs` storage: **NUMERIC(6,2)**

---

## 0) Reality check: what’s already in place

Today, the system already has the plumbing we need:
- Agent tool execution runs through API: `POST /internal/tools/execute`
- Agent learns tool + “table card” docs from API: `GET /capabilities` → agent writes `services/agent/app/generated/`
    - this is not abstract enough tho and is loaded in full context every time? 
- Realtime UI already uses: `WS /realtime` → API calls agent `POST /run`

So to add a new domain (weights), we extend **the same 3 seams**:
1) DB + model
2) tool executor (API)
3) tool schema + table card registry (API → /capabilities)

---

## 0.1) Abstraction concern: “/capabilities gets loaded in full context every time”

You’re correct: in the current implementation, the agent’s compiled instructions include *all* table cards every run.

What “abstract enough” should look like (conceptually):
- The *capability store* still lives in one place (`/capabilities` → `generated/`), because it’s auditable.
- The *prompt* should not automatically include everything.
- The agent should have a small base rule: “If you need weights/forms, request the weights/form card.”

This doc is about weights, but the design goal is general:
- Adding a new table adds **one** new card + tools.
- The base agent prompt stays stable.

Minimal mechanism to get there later:
- Add a tool like `capability_card_get({ id })` that returns a card’s markdown (or a structured form spec).
- Keep `generated/` as the cache/audit trail, but only load card(s) on demand.

For the weights MVP, we can keep the current “everything loaded” behavior, but we should:
- design weights so it’s a single **self-contained capability** (tools + card)
- not require any persona edits to “enable weights”

---

## 1) Data model

### 1.1 Table: `weight_entries`

Purpose: time-series weigh-ins, editable but still “measurement-like”.

Recommended columns:
- `id` UUID PK
- `user_id` UUID FK → `users.id` (cascade delete)
- `measured_at` timestamptz NOT NULL (editable)
- `weight_lbs` NUMERIC NOT NULL (canonical)
- `notes` text NULL
- `created_at`, `updated_at` timestamptz NOT NULL default `now()`

Indexes (minimum):
- `(user_id, measured_at DESC)` for “recent weights”

### 1.2 No “goal weight”

We leave it out entirely for now.

---

## 2) CRUD surface: tools first (not REST)

You asked for “full CRUD”. In this architecture, **tools are the CRUD surface**.

Tool set (names matter because they’re part of the contract):
- `weight_entry_list({ limit? })` (default limit=30)
- `weight_entry_create({ measuredAt, weightLbs, notes? })`
- `weight_entry_update({ id, measuredAt?, weightLbs?, notes? })`
- `weight_entry_delete({ id })`

Why this is enough:
- chat uses `create` (and sometimes `list`)
- editable form uses `list` + `update/delete/create`

Optional “token saver” tool (strongly recommended once forms exist):
- `weight_entry_save_batch({ entries: [...] })`
  - server treats this as “upsert these entries, delete missing ones, return canonical list”
  - enables “one click Save → one tool call” instead of N updates

---

## 2.1) Yes: `save_batch` should be part of the CRUD skill abstraction

Think of the “CRUD skill” for any table as a template that always includes:
- `list`, `create`, `update`, `delete`
- plus *one aggregation tool* (either `save_batch` or `apply_patchset`)

Reason: forms generate bursts of changes. Without an aggregation tool you end up with:
- lots of tool calls (slow + expensive)
- more token churn (each tool call adds tool logs + context)

So for weights specifically, `weight_entry_save_batch` is not a special case; it’s the standard “forms-friendly CRUD” tool.

Design note (to keep future tables fast):
- treat “CRUD + save_batch” as the default tool bundle for any editable table.

---

## 3) The table card: backend-generated (yes)

You want: “coach prompt doesn’t need much beyond ‘weights skill exists’ and ideally this comes from the backend.”

That’s exactly what your `/capabilities` system is for.

Mechanism in this repo:
- API generates `tableCards` from `RESOURCE_DEFS` (registry)
- Each resource has:
  - a Pydantic model (fields)
  - a Meaning section (semantics)
  - a tool mapping section (how to call tools)

So to add a “weights skill”, we:
1) define a `WeightEntryResource` Pydantic model
2) register it in `RESOURCE_DEFS` with a clear meaning + tool mapping

The agent service will sync and materialize it into `services/agent/app/generated/table_cards/weights.md` automatically.

---

## 3.1) “Can the tools be part of the tool card?” / “Can tools be part of the table card?”

You already have the right split in this repo:
- Tools (machine-readable): `services/api/app/agentic/openai_tools.py`
- Table cards (human-readable): generated markdown from `RESOURCE_DEFS`

What *should* be inside the table card:
- tool mapping (example call signatures)
- invariants and semantics (what does update mean, how to verify)
- import rules (how to parse pasted tables)

What should *not* be inside the table card as the only source of truth:
- the actual JSON Schema for tool parameters

Reason: the runner needs tool schemas in a strict format. Markdown is for humans and LLM guidance.

Practical compromise that keeps edits localized:
- Table card includes a “Supported tool mapping” section (you already generate this)
- Tools remain canonical in `openai_tools.py`
- Both are generated/updated from the same registry entry (so you edit one place)

Refinement (what we actually want):
- tools JSON schemas are generated from Pydantic tool-args models (no hand-written JSON)
- table card is generated from the same registry (no hand-written markdown)

---

## 4) Chat UX (coach)

### 4.1 Log a weigh-in
Example user text:
- “I weighed 182.4 this morning”

Coach behavior:
1) parse weight in lbs and measured_at
  - if date-only, assume 12:00 PM local time
2) call `weight_entry_create`
3) confirm

### 4.2 Show/edit weigh-ins
Example user text:
- “Show my weigh-ins” → `weight_entry_list`
- “Change yesterday to 183.0” → `weight_entry_update`

### 4.3 Open an editable form
Example user text:
- “Open my weights form”

Coach behavior (high-level):
1) call `weight_entry_list` (or rely on state/context if you later add it)
2) emit A2UI view tree for editing (or whatever UI contract is active)

---

## 5) Token concern: “coach turns actions into tool calls will waste tokens”

You’re right to worry. The fix is architectural, not prompt hacks.

### 5.1 Don’t do per-keystroke tool calls
The UI should NOT send an action for every keystroke that triggers a tool call.

Recommended pattern:
- UI edits are local (client state)
- Save button sends one action containing the entire draft
- Coach performs **one** tool call: `weight_entry_save_batch`

### 5.2 Keep agent prompts stable and small
- The weights “skill” should be delivered by backend via `/capabilities` table card + tools.
- Avoid adding “weights exist” lines to the persona. The persona should instead follow a stable rule:
  - “Only use tools and table cards provided by `/capabilities`; do not invent tools/tables.”

---

## 5.3) Forms: only tools on Save (not on every edit)

To keep both latency and tokens down:
- UI edits update local client state only.
- Only the Save button triggers an action that results in tool calls.
- Coach converts that single Save action into exactly one call:
  - `weight_entry_save_batch({ entries: [...] })`
- `save_batch` returns the canonical list that the UI re-renders.

This preserves the “agent is in charge” behavior without turning typing into tool spam.

Minimum A2UI needed for weights:
- a batch editor form with:
  - list of rows (measuredAt, weightLbs, notes)
  - add row / delete row
  - Save

---

## 6) Files to edit (and why) — with concrete snippets

Below are the minimal edit points that match current repo conventions.

### 6.1 DB migration (create table)
File: `services/api/alembic/versions/0005_create_weight_entries_table.py`

```py
"""create weight_entries table

Revision ID: 0005_create_weight_entries_table
Revises: 0004_add_password_hash_to_users
Create Date: 2026-01-07

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_create_weight_entries_table"
down_revision = "0004_add_password_hash_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weight_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight_lbs", sa.Numeric(6, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index(
        "weight_entries_user_measured_idx",
        "weight_entries",
        ["user_id", "measured_at"],
    )


def downgrade() -> None:
    op.drop_index("weight_entries_user_measured_idx", table_name="weight_entries")
    op.drop_table("weight_entries")
```

Why: this is the single source of truth for persistence.

### 6.2 SQLAlchemy model row
File: `services/api/app/models.py`

```py
class WeightEntryRow(Base):
    __tablename__ = "weight_entries"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    measured_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    weight_lbs: Mapped[sa.Numeric] = mapped_column(sa.Numeric(6, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    updated_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)

sa.Index("weight_entries_user_measured_idx", WeightEntryRow.user_id, WeightEntryRow.measured_at)
```

Why: consistent with existing `ProfileRow` and enables repo/service patterns.

### 6.3 Repository (DB queries)
File: `services/api/app/repositories/weight_entries_repo.py`

Responsibilities:
- list by user (ordered by measured_at desc)
- create
- update
- delete

Snippet style should match `ProfilesRepository`.

### 6.4 Service (domain layer)
File: `services/api/app/services/weight_entries_service.py`

Responsibilities:
- validate input shapes
- map DB rows → API dicts
- optionally enforce business rules (later)

Pattern should match `ProfilesService`.

### 6.5 Tool executor wiring
File: `services/api/app/services/tools_service.py`

Add cases:
```py
if name in ("weight_entry.list", "weight_entry_list"):
    ...
if name in ("weight_entry.create", "weight_entry_create"):
    ...
if name in ("weight_entry.update", "weight_entry_update"):
    ...
if name in ("weight_entry.delete", "weight_entry_delete"):
    ...
if name in ("weight_entry.save_batch", "weight_entry_save_batch"):
    ...
```

Why: this is the single place where agent side effects hit the DB.

Refinement (to avoid the “icky if/elif ladder” growing forever):
- replace the ladder with a registry dispatch table or a domain router.
- each domain (profiles, weights, next-table) owns its own handlers.

### 6.6 Tool schemas (what the model is allowed to call)
File: `services/api/app/agentic/openai_tools.py`

Add tool definitions:
```py
{
  "type": "function",
  "function": {
    "name": "weight_entry_create",
    "description": "Create a weigh-in entry (lbs).",
    "parameters": {
      "type": "object",
      "properties": {
        "measuredAt": {"type": "string", "description": "ISO timestamp"},
        "weightLbs": {"type": "number"},
        "notes": {"type": "string"}
      },
      "required": ["measuredAt", "weightLbs"],
      "additionalProperties": False
    }
  }
}
```

Why: this is your “runtime skill API”. If it’s not here, the agent can’t call it.

Refinement (so we don’t hand-write JSON):
- define Pydantic models for tool arguments (`WeightEntryCreateArgs`, etc.)
- generate the JSON schema via `model_json_schema()`
- wrap it into the OpenAI tool envelope

### 6.7 Table card model (fields) + registry entry (meaning)
Files:
- `services/api/app/resources/models.py`
- `services/api/app/resources/registry.py`

Add a Pydantic model:
```py
class WeightEntryResource(BaseModel):
    id: str = Field(description="UUID")
    userId: str = Field(description="UUID")
    measuredAt: str = Field(description="ISO timestamp (editable)")
    weightLbs: float = Field(description="Weight in lbs")
    notes: Optional[str] = Field(default=None)
```

Register it:
```py
"weights": ResourceDef(
  name="weights",
  model=WeightEntryResource,
  meaning="Weigh-in entries (lbs). Use measuredAt for backdating. Many per user.",
  primary_key="id (UUID)",
  tool_mapping={
    "List": "weight_entry_list({ limit: 30 })",
    "Create": "weight_entry_create({ measuredAt, weightLbs, notes? })",
    "Update": "weight_entry_update({ id, measuredAt?, weightLbs?, notes? })",
    "Delete": "weight_entry_delete({ id })",
    "SaveBatch": "weight_entry_save_batch({ entries: [...] })",
  },
)
```

Why: this is the *backend-authored* “weights skill” documentation that the agent syncs automatically.

### 6.8 Coach prompt changes (minimize this)
Goal: avoid per-table prompt edits.

Preferred stable persona rule:
- “Use only the tool surface and table cards published by `/capabilities`.”

If you still want an explicit weights mention, it should be auto-generated (e.g., in a compiled “capability index”), not hand-edited.

---

## 7) What we do NOT need to edit (yet)

- No need to change websocket transport (`WS /realtime`).
- No need to add REST endpoints for weights to get full CRUD (tools cover it).
- No need to implement full A2UI renderer right now to get the DB + tools + table card in place.

Refinement: you *do* need a minimal form renderer to satisfy “pull up a form and edit/save”.
You do **not** need every A2UI component; you need the batch editor subset only.

---

## 8) How adding the next table should feel (repeatable recipe)

For “the next table”, repeat this exact set:
1) alembic migration
2) `models.py` row
3) repo + service
4) tools wiring (`ToolsService` + `openai_tools.py`)
5) resource model + registry entry (table card)

That’s the minimal set of seams in this codebase.

Refinement goal (reduce edits-per-table):
- One registry entry should generate:
  - tool schemas
  - tool dispatch registration
  - table card markdown
Then the only remaining “manual” work per table is:
- DB migration + SQLAlchemy model

---

## 9) Open questions (only the ones that matter)

- Should `weight_entry_list` default to last 30 entries, or time range?
- Do you want `weight_lbs` stored as `NUMERIC(6,2)` (recommended) or integer ounces?
- When backdating, should `measured_at` accept date-only inputs (assume morning) or require full timestamp?

Answers:
- list: last 30
- numeric: NUMERIC(6,2)
- backdating: date-only allowed; default time = 12:00 PM local

---

## 10) Import scenario: user pastes a markdown table of weigh-ins

Example input (from `.dev/ks_notes2.md`):

| Entry | Date | AM/PM | Weight (lb) | Confidence | Notes |
|---:|---|:---:|---:|---|---|
| 1 | 12/25 | PM | 181.9 | High | first logged weigh-in |
| 2 | 12/30 | AM | 176.0 | Medium | date uncertain from earlier timeline |
...

What the coach should do:
1) Ask exactly one clarifying question *if needed*:
   - “What year are these dates in, and what timezone should I use?”
2) Parse rows into normalized entries:
   - `measuredAt`: combine date + AM/PM into a timestamp (choose a consistent hour, e.g. 08:00 for AM, 20:00 for PM)
   - `weightLbs`: float
   - `notes`: include confidence + notes (or store confidence separately later)
3) Avoid guessing destructive changes.

How to prevent accidental overwrites/deletes:
- Add one extra tool (recommended) for safe imports:
  - `weight_entry_import_preview({ entries: [...] })` → returns a diff: {creates, updates, conflicts}
- Coach presents the diff in plain language and asks confirmation.
- On confirm, coach calls `weight_entry_save_batch` (or a dedicated `import_apply`).

If you want *even fewer tokens*:
- Make `weight_entry_save_batch` accept `mode`:
  - `mode: "merge"` (default): upsert by id if present; otherwise create; never delete
  - `mode: "replace_range"`: replace entries within a computed date range (requires explicit confirmation)

This pattern generalizes to the next tables you add (it becomes part of the CRUD skill template).

---
