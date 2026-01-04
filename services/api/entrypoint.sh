#!/bin/sh
set -eu

# Run DB migrations before starting the API.
# This is intentionally simple: retry Alembic until Postgres is ready.

MAX_RETRIES="${DB_MIGRATE_MAX_RETRIES:-30}"
SLEEP_SECONDS="${DB_MIGRATE_SLEEP_SECONDS:-1}"

attempt=1
while :; do
  if alembic upgrade head; then
    echo "Migrations applied."
    break
  fi

  if [ "$attempt" -ge "$MAX_RETRIES" ]; then
    echo "Failed to apply migrations after ${MAX_RETRIES} attempts." >&2
    exit 1
  fi

  echo "Waiting for database... (attempt ${attempt}/${MAX_RETRIES})"
  attempt=$((attempt + 1))
  sleep "$SLEEP_SECONDS"
done

exec "$@"
