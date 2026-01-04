#!/bin/sh
set -eu

cd /app

# Ensure the local package (./app) is importable when Alembic runs.
export PYTHONPATH="/app${PYTHONPATH:+:$PYTHONPATH}"

# Run DB migrations before starting the API.
# This is intentionally simple: retry Alembic until Postgres is ready.

MAX_RETRIES="${DB_MIGRATE_MAX_RETRIES:-30}"
SLEEP_SECONDS="${DB_MIGRATE_SLEEP_SECONDS:-1}"

attempt=1
while :; do
  set +e
  out=$(alembic -c /app/alembic.ini upgrade head 2>&1)
  status=$?
  set -e

  if [ "$status" -eq 0 ]; then
    echo "Migrations applied."
    break
  fi

  # If this DB was created before Alembic was introduced, the schema objects may
  # already exist but the alembic_version table won't. In that case we can stamp
  # head so the API can boot without destroying data.
  if echo "$out" | grep -qiE "DuplicateTable|already exists"; then
    echo "Migrations indicate schema already exists; stamping head."
    alembic -c /app/alembic.ini stamp head
    break
  fi

  echo "$out" >&2

  if [ "$attempt" -ge "$MAX_RETRIES" ]; then
    echo "Failed to apply migrations after ${MAX_RETRIES} attempts." >&2
    exit 1
  fi

  echo "Waiting for database... (attempt ${attempt}/${MAX_RETRIES})"
  attempt=$((attempt + 1))
  sleep "$SLEEP_SECONDS"
done

exec "$@"
