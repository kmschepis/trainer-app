# Plan — 005-template-hardening

## 1) Inventory current state

- Confirm existing run commands in `.github/instructions/copilot-instructions.md` are correct.
- Confirm `compose.yml` boots and ports match README.

## 2) Decide the minimal template hardening set

Keep it minimal and broadly applicable:

- CI: build containers + run linters/tests
- Repo hygiene: `.env.example`
- Dependency automation: Dependabot
- Optional DX: Dev Container

## 3) Implement in small, verifiable chunks

- Add `.env.example` and document required env vars.
- Add GitHub Actions workflow(s):
  - install + lint/test `apps/web`
  - lint/test `services/api` and `services/agent`
  - optionally validate `docker compose config`
- Add Dependabot config.
- Optional: add `.devcontainer/` configuration.

## 4) Document release/versioning

- Add a short “Template tagging” section to the root README and/or a dedicated doc.

## 5) Verify

- CI passes on a clean checkout.
- Local commands mirror CI.
