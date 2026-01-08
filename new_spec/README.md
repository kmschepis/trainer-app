# new_spec — Trainer3 (Conceptual Target)

This folder is a **conceptual spec** for what we’re trying to build if we were not constrained by the current walking-skeleton implementation.

The point of this spec is:
- Keep sight of the tangible product: an **AI personal trainer app**.
- Treat “the AI coach” as a **feature** inside a larger platform.
- Design for **modularity** so new tables/forms/agents/skills can be added with minimal engineering effort.
- Design for **non-technical operators** to add/modify forms and flows safely.

## Reading order

1) [00-overview/00-vision.md](00-overview/00-vision.md)
2) [01-product/00-user-journeys.md](01-product/00-user-journeys.md)
3) [02-platform-architecture/00-system-map.md](02-platform-architecture/00-system-map.md)
4) [05-capabilities-and-skills/00-capability-registry.md](05-capabilities-and-skills/00-capability-registry.md)
5) [06-ui-and-a2ui/00-ui-contract.md](06-ui-and-a2ui/00-ui-contract.md)
6) [07-audit-and-approvals/00-coach-audit.md](07-audit-and-approvals/00-coach-audit.md)
7) [04-data-model/00-weights.md](04-data-model/00-weights.md)

## Glossary (short)

- **Capability**: something the system can do (tools + data model + UI + policy), versioned.
- **Skill**: an instruction + schema bundle the agent can load on-demand for a capability.
- **Tool**: a backend-executed action the agent can call (read/write).
- **A2UI**: a strict JSON UI contract the agent can emit, and the frontend can render.
- **Audit mode**: human-in-the-loop approvals for tool calls and responses.
