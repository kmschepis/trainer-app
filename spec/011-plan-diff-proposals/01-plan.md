# 011 — Plan

1. Define the plan diff schema:
   - `before_md`, `after_md`, `hunks[]`, `why`
2. Extend agent responses to optionally include a `planDiff`.
3. Extend API to relay plan diff and persist proposal as an event.
4. Add web UI to render the diff and capture user decision.
5. Update projection:
   - accepted diff updates current plan
6. Verify end-to-end with a deterministic “propose a small change” agent behavior.
