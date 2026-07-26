#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

MIGRATIONS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../src/db/migrations" && pwd)"

shopt -s nullglob
migrations=("$MIGRATIONS_DIR"/*.sql)

if (( ${#migrations[@]} == 0 )); then
  echo "No migrations found in ${MIGRATIONS_DIR}" >&2
  exit 1
fi

for migration in "${migrations[@]}"; do
  echo "Applying $(basename "$migration")"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$migration"
done

echo "Migrations complete"
