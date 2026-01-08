# Plan — 016 Auth and Multi-user

1. Add NextAuth (Auth.js) with Google provider in `apps/web/`.
2. Replace `/` with a landing page and move the existing coach UI to `/coach`.
3. Implement API auth:
   - Verify Google ID token (audience = `GOOGLE_CLIENT_ID`).
   - Upsert a `users` row.
4. Add `user_id` to `events`:
   - Alembic migration: create `users`, add `events.user_id`, add indexes.
   - Update repositories/services/routes to always write and query by `user_id`.
5. Wire Compose env vars, rebuild, and verify:
   - Login works.
   - `/coach` uses authenticated WS.
   - `/state` is user-scoped.
