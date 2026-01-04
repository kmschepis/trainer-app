# 008 — Agent Plan Generation (Week 1)

## Goal

Have the agent generate a **1-week plan markdown** from the onboarded profile, and persist it as events.

## Acceptance criteria

- Web can request “generate my plan”.
- API calls agent with current state snapshot.
- Agent returns plan markdown.
- API appends `PlanGenerated` event containing the markdown (or a reference).
- `GET /state` exposes the current plan markdown for UI rendering.

## Non-goals

- Perfect programming logic; the first cut can be deterministic/templated.
- Plan diffs (handled in Phase 2 unit).
