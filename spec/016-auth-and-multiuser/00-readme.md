# 016 — Auth and Multi-user

## User story
As a real user, I want to sign in (Google) so my profile/state is private to my account and multiple people can use the app on the same deployment.

## Scope
- Web: landing page for login/signup, Google sign-in, protected coach UI route.
- API: validate Google ID token, create/find user, associate events with user, and only return user-scoped state.

## Non-goals (for this unit)
- Team/org support.
- Password auth.
- Full RBAC.
- Advanced account linking.

## Acceptance criteria
- Visiting `/` shows a landing page with a Google sign-in button.
- Visiting `/coach` without being signed in redirects to `/`.
- After Google sign-in, `/coach` loads and the existing realtime chat/onboarding UI works.
- API rejects unauthenticated requests when `AUTH_REQUIRED=true`:
  - `GET /state` returns `401` without `Authorization: Bearer <google_id_token>`.
  - `WS /realtime` closes if `token` query param is missing/invalid.
- Events are stored with `user_id` and `/state?sessionId=...` only returns events for the authenticated user.

## External setup (required)
You must create Google OAuth credentials:
- Google Cloud Console → APIs & Services → Credentials → Create OAuth client ID (Web application)
- Authorized redirect URI: `http://localhost:3000/api/auth/callback/google`
- Provide env vars to the web container:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `NEXTAUTH_SECRET`
  - `NEXTAUTH_URL=http://localhost:3000`
