# 007 — Plan

1. Define onboarding schema (shared shape, web→API event payload).
2. Implement onboarding interview flow (chat-first UI is acceptable; form is optional).
3. Persist onboarding:
   - call API `POST /events` with `UserOnboarded` payload
4. Update state projection (unit 006) to include profile fields.
5. Verify:
   - complete onboarding interview
   - confirm profile appears in `GET /state`
