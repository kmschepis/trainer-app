# Dev scripts

## Reset Postgres (destructive)

This deletes the Docker volume backing Postgres and re-runs Alembic migrations.

- Bash (Git Bash / WSL):
  - `./.dev/scripts/reset_db.sh`
  - Non-interactive: `./.dev/scripts/reset_db.sh --yes`

- PowerShell:
  - `powershell -ExecutionPolicy Bypass -File .\.dev\scripts\reset_db.ps1`
  - Non-interactive: `powershell -ExecutionPolicy Bypass -File .\.dev\scripts\reset_db.ps1 --yes`
