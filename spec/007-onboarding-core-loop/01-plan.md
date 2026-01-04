# 007 — Plan

1. Define onboarding schema (shared shape, web→API event payload).
2. Add onboarding route/page in the web app.
3. On submit:
   - call API `POST /events` with `UserOnboarded` payload
4. Update state projection (unit 006) to include profile fields.
5. Verify:
   - submit onboarding
   - confirm profile appears in `GET /state`
