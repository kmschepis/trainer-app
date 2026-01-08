# Auth
- Unauthenticated users see a landing page with Google sign-in.
- Authenticated users can sign out from the app.

# Coach
- The coach UI is available at `/coach` and requires being signed in.
- The coach UI uses the realtime WebSocket endpoint after sign-in.

# Data isolation
- Profile and event state is scoped to the signed-in user.
- Requests without a valid auth token are rejected when auth is enabled.
