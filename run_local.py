#!/usr/bin/env python3
"""Run Todo MCP Chat FastAPI backend and Next.js dev servers together."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

# Script is at the repository root. If you move this file under scripts/, use:
#   ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"


def _load_dotenv(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE .env file; skips comments and blank lines."""
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _stop_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)


def main() -> int:
    if not BACKEND_DIR.is_dir():
        print(f"Missing backend directory: {BACKEND_DIR}", file=sys.stderr)
        return 1
    if not FRONTEND_DIR.is_dir():
        print(f"Missing frontend directory: {FRONTEND_DIR}", file=sys.stderr)
        return 1
    if shutil.which("uv") is None:
        print("uv not found on PATH — see https://docs.astral.sh/uv/", file=sys.stderr)
        return 1
    if shutil.which("npm") is None:
        print("npm not found on PATH — install Node.js.", file=sys.stderr)
        return 1

    base_env = os.environ.copy()
    dotenv_vars = _load_dotenv(ROOT / ".env")
    for key, value in dotenv_vars.items():
        base_env.setdefault(key, value)

    backend_env = base_env.copy()
    frontend_env = base_env.copy()

    host = (backend_env.get("HOST") or "0.0.0.0").strip() or "0.0.0.0"
    port_s = (backend_env.get("PORT") or "8000").strip() or "8000"
    try:
        port = int(port_s)
    except ValueError:
        print(f"Invalid PORT={port_s!r}; expected an integer.", file=sys.stderr)
        return 1

    backend_cmd = [
        "uv",
        "run",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--host",
        host,
        "--port",
        str(port),
    ]
    frontend_cmd = ["npm", "run", "dev"]

    if _port_in_use(port):
        print(
            f"WARNING: Something is already listening on port {port}. "
            "Uvicorn may fail to bind; the UI could still talk to that process (often an OLD API).",
            flush=True,
        )
        print(f"  Free the port:  lsof -ti :{port} | xargs kill -9  # macOS/Linux", flush=True)

    shell = os.name == "nt"
    backend = subprocess.Popen(
        backend_cmd,
        cwd=str(BACKEND_DIR),
        env=backend_env,
        shell=shell,
    )
    time.sleep(1)
    frontend = subprocess.Popen(
        frontend_cmd,
        cwd=str(FRONTEND_DIR),
        env=frontend_env,
        shell=shell,
    )

    display_host = "localhost" if host in ("0.0.0.0", "::", "[::]") else host
    print("Todo MCP Chat local dev started:", flush=True)
    print(f"- Backend:  http://{display_host}:{port}", flush=True)
    print("- Frontend: http://localhost:3000  (see package.json dev script for port)", flush=True)

    todo_db = (backend_env.get("TODO_DB_PATH") or "").strip()
    data_dir = (backend_env.get("DATA_DIR") or "").strip()
    if todo_db:
        print(f"- SQLite:   todos DB → {todo_db}", flush=True)
    elif data_dir:
        print(f"- SQLite:   DATA_DIR={data_dir} (todos under that folder by default)", flush=True)
    else:
        print("- SQLite:   default files under backend/data/ (set TODO_DB_PATH / DATA_DIR in .env to override)", flush=True)

    if (backend_env.get("CLERK_JWKS_URL") or "").strip():
        print("- Auth:     Clerk JWT verification enabled (CLERK_JWKS_URL set)", flush=True)
    else:
        print("- Auth:     anonymous / open API (no CLERK_JWKS_URL)", flush=True)

    print(
        "- CORS:     set CORS_ORIGINS in .env for production; empty uses dev defaults in api/main.py",
        flush=True,
    )
    print(flush=True)

    try:
        while True:
            bc = backend.poll()
            if bc is not None:
                print("\nBackend process exited.", flush=True)
                _stop_process(frontend)
                return int(bc)
            fc = frontend.poll()
            if fc is not None:
                print("\nFrontend process exited.", flush=True)
                _stop_process(backend)
                return int(fc)
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nStopping services...", flush=True)
        return 130
    finally:
        for proc in (backend, frontend):
            _stop_process(proc)


if __name__ == "__main__":
    sys.exit(main())
