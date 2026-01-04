# 008 — Plan

1. Define the agent request/response contract for plan generation.
2. Add an API endpoint (or WS message) to request plan generation.
3. Implement agent handler that:
   - reads profile from provided state
   - produces week-1 plan markdown
4. Append `PlanGenerated` event.
5. Update state projection to surface “current plan”.
6. Verify via web UI and `GET /state`.
