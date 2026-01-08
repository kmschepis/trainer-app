# System map

This defines the target runtime roles and boundaries.

## Components

- **Web UI**: renders A2UI view trees and sends user actions.
- **API Executor**: authoritative boundary; validates, authorizes, persists.
- **Agent Runtime**: produces plans, tool calls, and A2UI outputs.
- **Capability Registry**: stores versioned “skills” and contracts.
- **Audit Console**: approves/denies risky operations.

## High-level topology

```mermaid
flowchart LR
  User((User)) --> Web[Web UI]

  Web <--> API[API Executor]
  API <--> Agent[Agent Runtime]

  API <--> Registry[Capability Registry]
  Agent <--> Registry

  Auditor((Auditor)) --> Audit[Audit Console]
  Audit <--> API
```

## Runtime loop (conceptual)

```mermaid
sequenceDiagram
  participant U as User
  participant W as Web UI
  participant A as Agent
  participant X as API Executor
  participant R as Capability Registry
  participant C as Audit Console

  U->>W: message / action
  W->>A: input event

  A->>R: load skill (on-demand)
  R-->>A: skill bundle (tools + A2UI schemas + instructions)

  alt agent needs data
    A->>X: tool call (read)
    X-->>A: results
  end

  alt agent wants to write
    A->>X: tool call (write)
    opt audit required
      X->>C: approval request
      C-->>X: approve/deny
    end
    X-->>A: success/failure
  end

  A-->>W: A2UI view tree + text
  W-->>U: rendered UI + message
```

## Non-negotiables

- The agent **cannot** directly write to the DB.
- The UI **does not** interpret intent; it renders and reports user actions.
- Skill bundles are **versioned** and fetched **on-demand**.
