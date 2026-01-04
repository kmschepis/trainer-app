# 009 — Plan

1. Define minimal session identity (date-based or explicit `WorkoutStarted`).
2. Add a workout page that:
   - renders plan markdown
   - contains a set logger panel
3. On set submit:
   - call API `POST /events` with `SetLogged`
4. Update state projection to include:
   - today’s session
   - logged sets grouped by exercise
5. Add a simple rest timer widget (if in scope).
6. Verify by logging multiple sets and refreshing the page.
