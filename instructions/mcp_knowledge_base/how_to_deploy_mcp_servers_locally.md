# how_to_deploy_mcp_servers_locally

This guide explains how to run MCP-related services on your machine for **this assessment repository** (Todo MCP Chat) and notes generic patterns for other projects.

---

## 1. Install requirements

- Python 3.12+ (match `backend` toolchain)
- [uv](https://docs.astral.sh/uv/) — virtualenv + lockfile for `backend/`
- Node.js + npm — for `frontend/`

---

## 2. Environment (this repo)

- At the **repository root**: `cp .env.example .env` and edit (see `README.md`).
- Minimum for chat: **`OPENROUTER_API_KEY`**. For split dev: **`NEXT_PUBLIC_API_URL`** (e.g. `http://127.0.0.1:8000`).
- SQLite paths: **`DATA_DIR`**, **`TODO_DB_PATH`**, **`AGENT_DB_PATH`** — leave blank to use defaults under `backend/data/` (empty `KEY=` is treated as unset in `backend/api/main.py`).

---

## 3. Install dependencies

```sh
cd backend && uv sync
cd ../frontend && npm install
```

---

## 4. Run everything (this repo)

From the **repository root**:

```sh
python run_local.py
```

Or: `./scripts/dev.sh` (bash) / `./scripts/run-backend.sh` for API only — see **`README.md`**.

- **API:** `uv run uvicorn api.main:app --reload` with `cwd` = `backend/` (or use `run_local.py`, which sets `HOST`/`PORT` from env; default bind `0.0.0.0:8000` in `run_local.py`).
- **Frontend:** `npm run dev` in `frontend/` (port from `package.json`, typically 3000).
- **MCP:** The todo MCP server is **stdio** — started by the FastAPI app via `MCPServerStdio` when handling chat, not as a separate long-running HTTP service. To smoke-test the module alone: `cd backend && PYTHONPATH=. uv run python -m todo_mcp` (blocks on stdio; mainly for debugging).

---

## 5. Troubleshooting

- **CORS / OPTIONS 400:** Origin must be allowed — set **`CORS_ORIGINS`** on the API or rely on empty-default dev rules in `backend/api/main.py` (includes localhost, 127.0.0.1, and common LAN patterns when unset).
- **SQLite “unable to open database file”:** Ensure `.env` does not set `TODO_DB_PATH=` / `DATA_DIR=` / `AGENT_DB_PATH=` to empty strings without meaning; use defaults or real paths.
- **`uv` / `npm` not found:** Install and ensure they are on `PATH`.

---

## 6. Best practices

- One root `.env` for local dev; mirror secrets on each deployment platform (Vercel vs Python host) per `README.md`.
- Use `uv sync` in `backend/` after dependency changes; commit `uv.lock` when the team relies on it.

---

## Summary

- **This repo:** root `.env` → `uv sync` in `backend/` → `npm install` in `frontend/` → **`python run_local.py`** (or `scripts/dev.sh`). MCP over stdio is orchestrated by FastAPI, not a separate `uv run market_server.py` style process.
