# 012 — Plan

1. Implement/constants:
   - RPE chart table → `pct_1rm(reps, rpe)`
2. Derive per-set and per-day stress:
   - SSU per set and day
   - optional CSU
3. Implement EWMA:
   - ATL (7d), CTL (28d)
   - FB = CTL - ATL
4. Compute readiness score:
   - map inputs to 0–100
   - compute weighted readiness
   - categorize into bands
5. Expose computed metrics via `GET /state`.
6. Verify with synthetic events and a small UI readout.
