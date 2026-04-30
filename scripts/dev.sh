#!/usr/bin/env bash
# To be able to run backend (uv + uvicorn) and frontend (npm dev) together.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACK_PID=""
FRONT_PID=""

cleanup() {
  if [[ -n "${FRONT_PID}" ]] && kill -0 "${FRONT_PID}" 2>/dev/null; then
    kill "${FRONT_PID}" 2>/dev/null || true
  fi
  if [[ -n "${BACK_PID}" ]] && kill -0 "${BACK_PID}" 2>/dev/null; then
    kill "${BACK_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "==> API (uv): http://${HOST:-127.0.0.1}:${PORT:-8000}"
(cd backend && uv run uvicorn api.main:app --reload --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}") &
BACK_PID=$!

sleep 1

echo "==> Frontend: http://localhost:${FRONT_PORT:-3000}"
(cd frontend && npx next dev --turbopack -p "${FRONT_PORT:-3000}") &
FRONT_PID=$!

wait
