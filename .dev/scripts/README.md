# Dev scripts

## Reset Postgres (destructive)

This deletes the Docker volume backing Postgres and re-runs Alembic migrations.

- Bash (Git Bash / WSL):
  - `./.dev/scripts/reset_db.sh`
  - Non-interactive: `./.dev/scripts/reset_db.sh --yes`

- PowerShell:
  - `powershell -ExecutionPolicy Bypass -File .\.dev\scripts\reset_db.ps1`
  - Non-interactive: `powershell -ExecutionPolicy Bypass -File .\.dev\scripts\reset_db.ps1 --yes`

## Setup agent↔api keypair (recommended)

The API exposes `GET /capabilities` for the agent to sync tool schemas + table cards.
Because `.env` files are single-line, these scripts store keys as base64:

- `AGENT_PRIVATE_KEY_B64`
- `AGENT_PUBLIC_KEY_B64`

Scripts:

- Bash (Git Bash):
  - `./.dev/scripts/setup_agent_keys.sh`
- PowerShell:
  - `powershell -ExecutionPolicy Bypass -File .\.dev\scripts\setup_agent_keys.ps1`

Then:

- `docker compose up -d --build api agent`
- `curl -X POST http://localhost:9000/update`
