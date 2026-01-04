# 011 — Plan Diff Proposals (Phase 2)

## Goal

Implement the “no silent edits” rule:

- agent proposes a plan diff
- UI shows a git-style before/after
- user can Accept / Modify / Deny

## Acceptance criteria

- Agent can produce a structured `PlanDiffProposed` response.
- Web renders a diff panel with before/after markdown and hunks.
- User actions append one of:
  - `PlanDiffAccepted`
  - `PlanDiffDenied`
  - (optional) `PlanDiffModified`
- Accepting a diff results in an updated current plan in state.

## Non-goals

- Perfect diff algorithm; line-based diffs are fine.
