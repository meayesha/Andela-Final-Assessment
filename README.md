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
2. **Build settings:** set **Framework Preset** to **Next.js**. Leave **Output Directory** empty (default). Do **not** set it to `public` — that error means Vercel is treating the app like a static folder of HTML; Next.js outputs to `.next` (or `out/` only if you set `STATIC_EXPORT=true` on Vercel, in which case use **`out`**, not `public`).
3. In Vercel → **Environment Variables**, set **`NEXT_PUBLIC_API_URL`** to your deployed Python API base URL (e.g. `https://your-api.onrender.com`) for Production and Preview.
4. Put **`OPENROUTER_API_KEY`** (and optional **`OPENROUTER_MODEL`**, **`CORS_ORIGINS`**) on the **Python host**, not in Vercel. The app calls OpenRouter’s OpenAI-compatible API with Chat Completions (see `backend/api/openrouter.py`).
5. Set **`CORS_ORIGINS`** on the API to your Vercel URL(s), e.g. `https://your-app.vercel.app`, so the browser can call the API.

### Clerk (sign-in on Vercel)

Use **repo root `.env`** for local Next (`frontend/next.config.ts` loads `../.env`) and mirror the same variables on **Vercel**:

- **`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`**, **`CLERK_SECRET_KEY`**

On the **Python API host**, add:

- **`CLERK_JWKS_URL`** (Clerk Dashboard → JWT templates → Session token → JWKS URL) so the API can verify `Authorization: Bearer` from the browser.
- **`CLERK_ISSUER`** (optional, same screen).

When **`CLERK_JWKS_URL`** is set, protected API routes require a Clerk session JWT; todos and chat history are scoped by Clerk user id. When unset, the API stays open for anonymous sessions (local/demo).

The **Docker / Hugging Face** image ships **`frontend/docker-hf/`** (no Clerk SDK) because Clerk is incompatible with `output: 'export'`. Use **Vercel** for the authenticated UI.

Variable reference: **`.env.example`** at the repo root.

## Hugging Face Space (Docker)

1. Create a **Docker** Space and push this repo (root `Dockerfile` is used).
2. In **Space variables**, add `OPENROUTER_API_KEY` (and optionally `OPENROUTER_MODEL`, e.g. `openai/gpt-4o-mini`).
3. The platform sets `PORT`; the image runs uvicorn on that port and serves the Next export from `/` plus APIs under `/api`.
4. The Docker build uses **`frontend/docker-hf/`** for the static UI (no Clerk). For Clerk + static export limitations, deploy the **frontend to Vercel** and the API elsewhere if you need sign-in on the same domain as static files.

## Layout

| Path | Role |
|------|------|
| `backend/todo_mcp/` | FastMCP stdio server + SQLite todo store |
| `backend/api/main.py` | FastAPI: MCP stdio client, agent streaming, `/api/todos`, history |
| `frontend/` | Next.js static export, chat + todo sidebar |

See `problem_statement.md` for the full assessment brief.
