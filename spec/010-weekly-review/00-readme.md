# 010 — Weekly Review

## Goal

Render a weekly review summary derived from events/state:

- adherence
- training load summary
- PRs / e1RM trend (basic)
- weight trend (basic)

## Acceptance criteria

- Web provides a weekly review page.
- API provides enough derived state to render the review.
- Review includes at least:
  - count of sessions / sets logged
  - latest and 7-day avg weight (if weight events exist)
  - e1RM estimate for at least one main lift (if sets exist)

## Non-goals

- Advanced charting; basic visualization is fine.
- Full fatigue model (separate unit).
