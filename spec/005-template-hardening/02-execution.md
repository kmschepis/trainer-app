# Execution log — 005-template-hardening

- Created `spec/005-template-hardening/` with `00-readme.md`, `01-plan.md`, `02-execution.md`.

## Implemented

- Added local env template: `.env.example`.
- Updated `compose.yml` to use env var substitution (defaults preserved) so `.env` overrides work without editing Compose.
- Added Dependabot automation: `.github/dependabot.yml`.
- Added CI workflow: `.github/workflows/ci.yml`.
	- Validates Compose config.
	- Web: installs, lints, builds.
	- Python: installs deps, runs `ruff`, runs `compileall`.
- Added minimal web lint configuration:
	- `apps/web/.eslintrc.json`
	- `apps/web/package.json` adds `lint` script + eslint deps.
- Added Python lint configuration: `pyproject.toml` (ruff).
- Fixed agent pydantic model default to avoid mutable-default pitfalls.
- Updated README with a short template-versioning note.
- Added `Makefile` with common shortcuts (build/check/new-branch/tag).

## Notes

- CI uses `npm install` (not `npm ci`) because there is currently no lockfile in `apps/web/`.
