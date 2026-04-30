#!/usr/bin/env bash
# We are starting the FastAPI app with uv (creates/uses backend/.venv).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"
exec uv run uvicorn api.main:app --reload --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}"

