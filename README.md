---
title: Todo MCP Chat
emoji: 📋
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Andela Final Assessment — Todo MCP Chatbot

MCP (Python) + OpenAI Agents SDK + Next.js chat UI. The LLM is called through **OpenRouter** (OpenAI-compatible Chat Completions). Todos live in SQLite; the agent talks to the MCP server over stdio; the browser streams assistant tokens over SSE.

## Local development

**1. Environment:** create `.env` at the **repository root** (next to `.env.example`).

```bash
cp .env.example .env
# Edit .env — at minimum set OPENROUTER_API_KEY (see https://openrouter.ai/keys)
```

The API loads this file automatically (`backend/api/main.py` resolves the repo root and runs `load_dotenv` on `.env`).

**2. Backend** (from repo root) with **[uv](https://docs.astral.sh/uv/)**:

```bash
cd backend
uv sync
# Repo-root .env is loaded by the app; ensure OPENROUTER_API_KEY (and optional Clerk keys) are set there.
uv run uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Or from the repo root: **`./scripts/run-backend.sh`** (same command; honors `HOST` / `PORT` env vars).

**Run API + Next together:** from repo root, **`./scripts/dev.sh`** (backend via `uv`, frontend on port **3000** by default; set **`FRONT_PORT`**, **`PORT`**, or **`HOST`** if you need overrides). **Ctrl+C** stops both.

**3. Frontend** (second terminal):

```bash
cd frontend
# Root `.env` is loaded automatically. For API on another port, set NEXT_PUBLIC_API_URL there.
npm install
npm run dev
```

**4. Single origin (like production):** build the UI into `backend/static`, then only run uvicorn.

```bash
cd frontend && npm run build
node scripts/copy-static.mjs   # copies out/ → ../backend/static
cd ../backend && PYTHONPATH=. uvicorn api.main:app --port 8000
```

Open `http://127.0.0.1:8000` — leave `NEXT_PUBLIC_API_URL` empty so the browser calls the same host.

## Vercel (frontend)

This app’s **agent and MCP stack run in Python** (FastAPI), not in Vercel’s Node runtime. On Vercel you typically deploy **only `frontend/`**:

1. New Vercel project → import this repo → set **Root Directory** to `frontend`.
2. **Build settings:** set **Framework Preset** to **Next.js**. Leave **Output Directory** empty (default). Do **not** set it to `public` or **`out`** unless you really use a static export — if Vercel serves only static files, **`/api/*` route handlers never run** and you will see **404** on todos/history. This repo’s **`frontend/vercel.json`** sets `"framework": "nextjs"` to nudge the correct build. Do **not** set **`STATIC_EXPORT=true`** on Vercel (it is for the Docker/HF image only); `next.config.ts` now ignores it when **`VERCEL=1`** so previews recover, but remove it to avoid confusion.
3. Point the browser at your Python API in one of two ways (Production **and** Preview):
   - **`NEXT_PUBLIC_API_URL`** — full API origin (e.g. `https://your-space.hf.space`). The client calls that host directly; set **`CORS_ORIGINS`** on the API to allow your `*.vercel.app` origin.
   - **`API_PROXY_ORIGIN`** (or **`NEXT_PUBLIC_API_URL`** on the server only) — same URL; **`frontend/app/api/*/route.ts`** handlers proxy same-origin **`/api/*`** at **request time** (good for **Preview** when the client bundle has no `NEXT_PUBLIC_*`). Leave **`NEXT_PUBLIC_API_URL`** empty in the client if you rely on this. The Docker image **removes** `app/api` before static export so Hugging Face builds are unchanged. **`next.config.ts`** uses **`trailingSlash: false`** so `/api/todos` is not rewritten to a trailing slash that can **404** on Vercel.
4. Put **`OPENROUTER_API_KEY`** (and optional **`OPENROUTER_MODEL`**, **`CORS_ORIGINS`**) on the **Python host**, not in Vercel. The app calls OpenRouter’s OpenAI-compatible API with Chat Completions (see `backend/api/openrouter.py`).
5. If you use **`NEXT_PUBLIC_API_URL`** (cross-origin from the browser), set **`CORS_ORIGINS`** on the API to your Vercel URL(s), e.g. `https://your-app.vercel.app`. With **`API_PROXY_ORIGIN`** only, the browser talks to Vercel first, so CORS from the browser to HF is not required for `/api/*`.

### Clerk (sign-in on Vercel)

Use **repo root `.env`** for local Next (`frontend/next.config.ts` loads `../.env`) and mirror the same variables on **Vercel**:

- **`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`**, **`CLERK_SECRET_KEY`**

On the **Python API host**, add:

- **`CLERK_JWKS_URL`** (Clerk Dashboard → JWT templates → Session token → JWKS URL) so the API can verify `Authorization: Bearer` from the browser.
- **`CLERK_ISSUER`** (optional, same screen).

When **`CLERK_JWKS_URL`** is set, the API verifies `Authorization: Bearer` when present. On **Hugging Face Spaces** (detected via `SPACE_ID`, `SPACE_REPO_NAME`, `SPACE_HOST`, etc.), missing Bearer falls back to **anonymous** `session_id` (docker-hf has no Clerk) unless you set **`CLERK_AUTH_STRICT=1`**. The **Dockerfile** also sets **`CLERK_AUTH_OPTIONAL=1`** so anonymous works even if a given Space omits HF env vars. Outside HF, missing Bearer returns **401** unless you set **`CLERK_AUTH_OPTIONAL=1`**.

When **`CLERK_JWKS_URL`** is unset, the API stays open for anonymous sessions (local/demo).

The **Docker / Hugging Face** image ships **`frontend/docker-hf/`** (no Clerk SDK) because Clerk is incompatible with `output: 'export'`. Use **Vercel** for the authenticated UI, or enable **`CLERK_AUTH_OPTIONAL`** on the Space if you keep JWKS for cross-origin Vercel calls.

Variable reference: **`.env.example`** at the repo root.

## Hugging Face Space (Docker)

1. Create a **Docker** Space and push this repo (root `Dockerfile` is used).
2. In **Space variables**, add `OPENROUTER_API_KEY` (and optionally `OPENROUTER_MODEL`, e.g. `openai/gpt-4o-mini`). If you copied **`CLERK_JWKS_URL`** from Vercel, either **pull the latest API code** (anonymous is default when HF sets `SPACE_ID`) or remove Clerk URL vars / set **`CLERK_AUTH_OPTIONAL=1`**. Otherwise an older image still returns **401** without Bearer.
3. The platform sets `PORT`; the image runs uvicorn on that port and serves the Next export from `/` plus APIs under `/api`.
4. The Docker build uses **`frontend/docker-hf/`** for the static UI (no Clerk). For Clerk + static export limitations, deploy the **frontend to Vercel** and the API elsewhere if you need sign-in on the same domain as static files.

## Layout

| Path | Role |
|------|------|
| `backend/todo_mcp/` | FastMCP stdio server + SQLite todo store |
| `backend/api/main.py` | FastAPI: MCP stdio client, agent streaming, `/api/todos`, history |
| `frontend/` | Next.js static export, chat + todo sidebar |

See `problem_statement.md` for the full assessment brief.
