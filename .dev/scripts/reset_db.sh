#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "$ROOT_DIR"

PROJECT_NAME="${COMPOSE_PROJECT_NAME:-$(basename "$ROOT_DIR")}"
DB_VOLUME="${PROJECT_NAME}_db_data"

YES="${1:-}"
if [[ "$YES" != "--yes" ]]; then
  echo "WARNING: This will DELETE the Postgres data volume: $DB_VOLUME"
  echo "All database data will be lost."
  echo
  read -r -p "Type 'reset' to continue: " CONFIRM
  if [[ "$CONFIRM" != "reset" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

echo "Stopping db container (if running)..."
docker compose -f compose.yml stop db >/dev/null 2>&1 || true

echo "Removing db container (if present)..."
docker compose -f compose.yml rm -f db >/dev/null 2>&1 || true

echo "Removing volume $DB_VOLUME (if present)..."
docker volume rm -f "$DB_VOLUME" >/dev/null 2>&1 || true

echo "Starting db..."
docker compose -f compose.yml up -d db

echo "Waiting for Postgres to accept connections..."
POSTGRES_USER="${POSTGRES_USER:-trainer}"
for i in {1..30}; do
  if docker compose -f compose.yml exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1; then
    break
  fi
  sleep 1
  if [[ $i -eq 30 ]]; then
    echo "Postgres did not become ready in time."
    exit 1
  fi
done

echo "Running Alembic migrations..."
docker compose -f compose.yml run --rm api alembic upgrade head

echo "Done. DB reset and migrated."
