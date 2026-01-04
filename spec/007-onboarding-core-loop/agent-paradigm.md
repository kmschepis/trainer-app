# Decision: Tool-Using Agent with Domain Tools (API-authoritative, event-sourced)

## Summary (chosen paradigm)

Use a **tool-using agent** that can take actions, but **only through constrained, domain-specific tools** executed by the **API** (the system boundary). The database remains **event-sourced** (append-only), and the agent’s actions **result in events** (e.g., `UserOnboarded`, `FoodLogged`, `WorkoutPlanned`).

In short:

- **Agent**: reasoning + planning + natural-language chat + chooses actions.
- **API**: validates + executes tools + persists events + serves derived state.
- **DB**: append-only event log (audit trail).
- **Web**: renders state and performs deterministic UI actions (A2UI).

This is the preferred method because it gives you agent “agency” without giving the model direct write access to your database.

## Why this is preferred

### 1) Safety and auditability (non-negotiable)
If the agent can write arbitrary events, you’ll eventually get:

- invalid event payloads,
- inconsistent state,
- hard-to-debug behavior,
- unsafe actions (“I updated your profile”) without user intent.

Constrained domain tools keep an audit trail while preventing the agent from inventing writes.

### 2) Better product semantics than `event.append(type, payload)`
A raw `event.append` tool is too generic. It forces the model to understand low-level storage and schema details.

Instead, expose tools that match product intent:

- `profile.save(profileDraft)` → API appends `UserOnboarded`
- `food.log(entry)` → API appends `FoodLogged`
- `workout.plan.generate(inputs)` → API appends `PlanGenerated`
- `workout.set.log(set)` → API appends `SetLogged`

These tools are easier for humans to reason about, easier to validate, and evolve cleanly.

### 3) UI control stays deterministic (A2UI)
A2UI is a separate channel:

- The agent can emit **UI actions** (open/patch/close forms, toast, navigate).
- The web applies them deterministically.
- The API can optionally gate them (e.g., only allow onboarding form actions pre-onboarding).

This keeps UI predictable while still being “agent-driven”.

## Compare/contrast

### Approach A — “Agent is read-only; UI/system writes all events”
**What it is**: agent only chats; backend persists based on explicit user actions.

- Pros: simplest, safest.
- Cons: agent can’t really act; you end up hardcoding orchestration logic in the backend.

### Approach B — “Agent can call `event.append(type, payload)` directly”
**What it is**: model requests raw event writes.

- Pros: fast to prototype.
- Cons: too much power + schema coupling; higher risk of garbage events; harder to validate/secure.

### Approach C — “Agent calls domain tools; API appends events” (chosen)
**What it is**: agent requests actions in product language; API validates and converts to events.

- Pros: agent can act; API stays authoritative; events remain clean/auditable; easier to evolve.
- Cons: requires a little upfront structure (tool schemas + validators).

## Practical implications for Unit 007 (Onboarding)

- The web can continue to send `ONBOARDING_SUBMIT` with a draft in context.
- The agent can respond with:
  - a confirmation message,
  - optional A2UI actions,
  - and (if the draft is complete) a tool call like `profile.save({...})`.
- The API executes `profile.save`, validates payload, and appends `UserOnboarded`.

## Notes on MCP

MCP is a great way to package tools later, but it’s not required for this decision.

- **Now**: implement tools inside the API (simple, direct, fast).
- **Later**: if you want tool reuse across different agent runtimes, expose the same tools via MCP.
