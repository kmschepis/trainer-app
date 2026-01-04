# 005-template-hardening

## Goal

Make this repository a reusable **agentic project template** by adding the missing “project skeleton” pieces that reduce friction for new work and keep quality high.

This unit is intentionally about *framework/skeleton* items (tooling, guardrails, CI), not product features.

## Context

We already have:

- A runnable Compose-based walking skeleton (`compose.yml`) with web/api/agent/db.
- Realtime transport (WS envelope) and an agent placeholder.
- A production-shaped observability baseline (Prometheus/Grafana/Loki/Tempo + OTel Collector).
- Spec-unit workflow governance in `spec/`.

What’s missing for a generalized template are the usual cross-cutting “starter kit” pieces: CI checks, local developer conveniences, and minimal release/versioning conventions.

## Proposed scope (pick minimal, but complete)

- **Repo hygiene**
  - `.env.example` (document required env vars; no secrets)
  - Optional: `scripts/` for common commands (Windows-friendly)

- **Quality gates**
  - CI pipeline (GitHub Actions) to build containers and/or run linters/tests
  - Formatting + linting for web and python services

- **Dependency and security automation**
  - Dependabot (or equivalent) for Docker/Node/Python
  - Basic secret scanning via GitHub defaults (no custom scanners unless needed)

- **Developer experience**
  - Optional: Dev Container configuration (VS Code) so contributors can onboard fast

- **Release conventions**
  - Document how to tag template versions (e.g., `template1`) and what that means

## Acceptance criteria

- A new contributor can follow a small set of documented commands to:
  - boot the stack,
  - run whatever CI would run locally,
  - and understand how to version a template release.
- CI exists and is green on a clean checkout.
- No secrets are committed; environment variables are documented via `.env.example`.
- All changes are recorded in this unit’s `02-execution.md`.
