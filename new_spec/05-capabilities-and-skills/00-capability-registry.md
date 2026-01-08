# Capability registry

The registry is the source of truth for what the platform can do.

## What a capability includes

A capability version bundles:
- **Data model contract** (tables/fields/validation)
- **Tool contract** (names + schemas + policies)
- **UI contract** (A2UI schemas + default views)
- **Skill docs** (agent-facing instructions and examples)

## Why a registry

- Makes the platform discoverable for agents and UIs.
- Enables on-demand loading (smaller prompts).
- Enables governance (permissions, approvals, rollbacks).

## Versioning

- Every capability has a `capability_id` and `version`.
- The agent requests a capability by ID + version range (e.g. latest compatible).
- The API Executor enforces that tool calls are from an allowed version.

## Publishing workflow (conceptual)

```mermaid
flowchart LR
  Draft[Draft in Studio] --> Validate[Validate\n(schemas + policies)]
  Validate --> Publish[Publish version vN]
  Publish --> Registry[Registry]
  Registry --> Runtime[Agent + UI load on-demand]
```

## “Table cards” and “skills”

- **Table cards**: concise, user-safe summaries (fields + semantics + examples).
- **Skills**: agent-facing instructions for when/how to use a capability.

The agent should load:
- table cards when it needs to understand a data domain
- skill docs when it needs to execute a workflow
