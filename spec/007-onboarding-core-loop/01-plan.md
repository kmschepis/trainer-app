# 007 — Plan

1. Define onboarding schema (shared shape, web→API event payload).
2. Implement onboarding interview flow (chat-first UI is acceptable; form is optional).
3. Persist onboarding (preferred):
   - agent requests a constrained domain tool (e.g. `profile.save(...)`)
   - API validates and appends `UserOnboarded`
   - (fallback during early dev: UI can call `POST /events` directly)
4. Update state projection (unit 006) to include profile fields.
5. Verify:
   - complete onboarding interview
   - confirm profile appears in `GET /state`
