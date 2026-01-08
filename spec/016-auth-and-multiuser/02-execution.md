# Execution log — 016 Auth and Multi-user

- Started unit.
- Added NextAuth (Google) scaffolding and a landing page at `/`.
- Moved the coach UI to `/coach` and started passing a Google ID token to API `/state` and WS via `?token=...`.
- Added a sign-out button in the coach UI.
- Added API-side Google ID token verification and a `users` table; events now have optional `user_id` and can be queried by `(user_id, session_id)`.
- Wired auth env vars into Compose and the `.env` template.
- Updated `compose.yml` so `web` and `api` containers receive `GOOGLE_CLIENT_ID`, and `web` receives NextAuth env vars.

## Commands / verification

- `AUTH_REQUIRED=false docker compose up --build -d`
- `curl http://localhost:8000/health` (200)
- `curl "http://localhost:8000/state?sessionId=test"` (200)

## User profile fields

- Extended onboarding draft + UI to capture first/last name, email, and phone.
- Prefilled first/last/email from the Google session when available and persisted `threadId` in localStorage per user.

## SQL-backed profiles

- Added a `profiles` table (one row per user) and a migration `0003_create_profiles_table`.
- Updated `profile_save` / `profile_delete` to upsert/delete from SQL (and still emit `ProfileSaved`/`ProfileDeleted` events for audit/back-compat).
- Updated `/state` and WS boot snapshot to prefer the SQL profile over event-sourced profile payload.
- Refactored the onboarding drawer to render fields from a small config list to reduce code churn when adding new fields.

## Chat markdown + multiline

- Updated the chat composer to a multiline textarea (`Shift+Enter` newline, `Enter` send).
- Updated chat message rendering to support Markdown (GFM) safely (no raw HTML), including multiline line breaks.

## Skill-driven DB management (foundation)

- Added a `db-manager` skill with table-card docs (starting with `profiles`) under `services/api/app/instructions/skills/db-manager/**`.
- Added read-only agent tools `list_skills` and `load_skill_file` plus `profile_get` so the coach can discover/load skills and verify writes.
