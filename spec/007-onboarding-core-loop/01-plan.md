# 007 — Plan

1. Confirm the onboarding contract (minimal fields + meaning).
   - Reuse the existing web onboarding draft shape as the initial payload.
2. Define the first constrained domain tool:
   - `profile.save(profile)`
   - Executed by the API (system boundary), persists a `UserOnboarded` event.
3. Teach the agent to drive onboarding using chat + A2UI:
   - If `context.hasProfile` is false, request the onboarding drawer open via `a2uiActions`.
   - If user submits (`message == "ONBOARDING_SUBMIT"` and `context.onboarding.submit == true`):
     - validate draft at a high level (ask for missing fields),
     - otherwise request the tool call `profile.save`.
4. Implement tool execution in the API websocket flow:
   - Parse tool calls returned by the agent.
   - Validate + execute `profile.save` (append `UserOnboarded`).
   - Return chat confirmation + A2UI actions (toast + close drawer).
5. Verify end-to-end:
   - Fresh DB: chat triggers onboarding drawer
   - Submit onboarding: `UserOnboarded` event exists
   - `GET /state` shows `snapshot.profile`
   - Subsequent chat sees `context.hasProfile == true`
