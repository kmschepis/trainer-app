# Vision

We are building an AI personal trainer application where:
- the AI coach is a *first-class UX* (chat + structured UI), but
- the platform is designed so the “coach” can safely operate over **real product capabilities** (data + forms + workflows).

This is not “a chatbot that can call a DB”. It’s:
- a product with **domain modules** (weights, workouts, nutrition, check-ins, etc.)
- a **capability registry** that makes those modules discoverable and governable
- a **UI contract** (A2UI) so the coach can present editable forms
- a **human approval console** to make iteration safe

## Core outcomes

- Users can log things by chat *or* by UI.
- Users can always review/edit what the coach is about to change.
- New features can be added as **capabilities** without rewriting the runtime.

## Key design constraints (product-grade)

- **Trust boundary**: only the backend executes side effects.
- **Contracts are versioned**: tools, data schemas, and UI schemas change in a controlled way.
- **On-demand context**: the agent loads skill docs only when needed.
- **Operator-friendly**: a non-technical user can add a form/table/flow via a Studio.

## Mental model

```mermaid
flowchart LR
  subgraph Studio[Studio (non-technical)]
    DSL[Capability DSL\n(forms, tables, policies)]
  end

  subgraph Platform[Platform]
    Registry[Capability Registry]
    API[API Executor]
    Agent[Agent Runtime]
    UI[UI Renderer]
    Audit[Audit Console]
  end

  DSL --> Registry
  Registry --> API
  Registry --> Agent
  Registry --> UI
  Audit --> API

  Agent -->|tool calls| API
  Agent -->|A2UI view tree| UI
  UI -->|user actions| Agent
```

## Why this spec exists

The current repo is a walking skeleton. This spec describes the *target state* so we don’t bake in accidental complexity while iterating.
