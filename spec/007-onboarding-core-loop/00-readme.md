# 007 — Onboarding (Core Loop)

## Goal

Create a minimal onboarding interview UI that produces an initial profile and persists it as events.

## Acceptance criteria

- Web provides an onboarding form capturing the MVP fields (goals, experience, constraints, metrics, diet prefs, risk flags).
- Submitting onboarding appends a `UserOnboarded` (or equivalent) event via the API.
- `GET /state` reflects the onboarded profile.
- The agent can be invoked after onboarding with the profile present in state.

## Non-goals

- Polished UI, validation beyond basic required fields.
- Auth.
