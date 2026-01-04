# 012 — Fatigue Analytics + Readiness Bands

## Goal

Implement the fatigue math described in the initial spec (SSU/CSU, ATL/CTL, readiness bands) and surface it in state for coaching and UI.

## Acceptance criteria

- API computes (from events/state):
  - e1RM estimate(s)
  - lifting stress (SSU)
  - optional conditioning stress (CSU)
  - ATL/CTL (EWMA)
  - fatigue balance (FB)
  - readiness score and band
- Web displays at least readiness band and a basic trend.
- Thresholds produce a clear “fatigue warning” signal in state.

## Non-goals

- Wearables integration.
- Highly personalized models.
