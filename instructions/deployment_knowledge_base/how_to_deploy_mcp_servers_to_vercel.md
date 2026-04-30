# how_to_deploy_mcp_servers_to_vercel

This guide covers **(A) how this assessment repository deploys**, and **(B) a generic legacy pattern** (Next + Python colocated on Vercel) for other projects.

---

## A. This repository (Todo MCP Chat — use this first)

**Do not** run the “`temp/` Next app merged to repo root + `/api/index.py`” bootstrap here. This repo is already:

- **`frontend/`** — Next.js 15 **App Router**. On Vercel, set **Root Directory** to `frontend`.
- **`backend/`** — FastAPI (`api.main:app`), OpenRouter + Agents SDK, **stdio MCP** (`todo_mcp`), **SQLite**. Run this API on a **container/VM** (root **`Dockerfile`**, e.g. Hugging Face Space), not as a tiny Vercel-only serverless replacement for the whole stack.
- **Root `.env`** — Loaded by the API from repo root; Next reads `../.env` via `frontend/next.config.ts`. Put **`OPENROUTER_API_KEY`** on the Python host only; set **`NEXT_PUBLIC_API_URL`** to the API’s public URL on Vercel; set **`CORS_ORIGINS`** on the API to your Vercel site origin(s).

**Local dev:** `python run_local.py` or `./scripts/dev.sh` from repo root — see **`README.md`**.

For the full checklist (Clerk, HF, SQLite caveats), read **`README.md`** before the sections below.

---

## B. Generic / legacy: additional files and folders (other repos)

For a **greenfield** monorepo on Vercel (not this repo’s `frontend/` + `backend/` split), you may include:

- `vercel.json` — routing/build config (see below)
- `.vercelignore`, `.gitignore`
- `requirements.txt` and `pyproject.toml` — Python dependencies
- `package.json` — Node.js dependencies
- `/api` — Python FastAPI backend (legacy serverless entry, e.g. `index.py`)
- `/pages` or `/app` — Next.js frontend
- `/public`, `/styles` — assets / CSS as needed
- `.env` and `.env.local` — environment variables (never commit)

If you bootstrap a new app with `create-next-app` in a `temp/` folder, merge into your chosen layout **outside** this assessment repo, or use a new repository.

The sections below walk through that **generic** full-stack-on-Vercel shape and Docker notes. **This assessment repo** should follow **section A** and root **`README.md`** instead.

---

## 1. Prerequisites

- Vercel account ([vercel.com](https://vercel.com/))
- Node.js (for Next.js frontend)
- Python 3.12+ (for FastAPI backend/MCP server)
- `uv` for Python environment management
- `vercel` CLI (`npm i -g vercel`)
- GitHub/GitLab/Bitbucket repo

---

## 2. Project structure (generic full-stack on Vercel)

```bash
/
├── api/                # Python FastAPI MCP backend (entry: index.py)
│   └── index.py
├── pages/              # Next.js frontend (entry: index.tsx, _app.tsx, etc.)
│   └── ...
├── public/             # Static assets
├── styles/             # Tailwind/global CSS
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
├── pyproject.toml      # Python project config
├── vercel.json         # Vercel routing/build config
├── .env                # Python env vars (not committed)
├── .env.local          # Next.js/Frontend env vars (not committed)
├── .gitignore
├── .vercelignore
├── Dockerfile          # (Optional) For non-Vercel/container deployments
└── README.md
```

**Key points:**

- Place all Python API code in `/api` (e.g., `/api/index.py`)
- Place all frontend code in `/pages` (Next.js Pages Router)
- Do NOT use `/pages/api` for backend if using Python—delete it if present

---

## 3. Required Files

### `vercel.json`

```json
{
  "rewrites": [{ "source": "/api/(.*)", "destination": "/api/index.py" }]
}
```

- Ensures all `/api/*` requests go to your Python FastAPI backend.

### `.vercelignore`

```bash
.env
node_modules
.next
.venv
__pycache__
*.pyc
*.pyo
Dockerfile
.dockerignore
```

- Prevents unnecessary files from being uploaded to Vercel.

### `.gitignore`

```bash
.env
.env.local
.venv
__pycache__/
*.pyc
*.pyo
node_modules/
.next/
```

---

## 4. Backend (Python MCP/FastAPI)

- Use FastAPI for HTTP endpoints (Vercel does not support stdio servers).
- Example: `/api/index.py`

  ```python
  from fastapi import FastAPI
  app = FastAPI()

  @app.get("/api/hello")
  def hello():
      return {"msg": "Hello from MCP FastAPI backend!"}
  ```

- Add all dependencies to `requirements.txt` and `pyproject.toml`.
- For streaming, auth, and Pydantic patterns in **this repo**, see `backend/api/main.py`, `backend/api/clerk_auth.py`, and `instructions/agents_knowledge_base/`.

---

## 5. Frontend (Next.js)

**Generic pattern (this section):** Pages Router at repo root, fetches **relative** `/api/*` when Python is routed on the same Vercel project.

**This repository:** App Router under **`frontend/app/`**; the browser calls the **external** API base from **`NEXT_PUBLIC_API_URL`** (absolute URL to your FastAPI host).

- Use `"use client"` where you need hooks and browser APIs.
- For authentication, streaming, and UI patterns here, see **`frontend/app/`** and `instructions/agents_knowledge_base/`.

---

## 6. Environment Variables

- Add secrets (API keys, etc.) in Vercel dashboard for both frontend and backend.
- Use `.env` for Python, `.env.local` for Next.js (never commit these).

---

## 7. Install and Build

- Install Node.js dependencies: `npm install`
- Install Python dependencies: `uv pip install -r requirements.txt`
- Build frontend: `npm run build` (Vercel does this automatically)
- No need to build Python—Vercel runs it as a serverless function.

---

## 8. Deploy

- Push to your Git repo.
- Connect repo to Vercel.
- Vercel auto-detects both Next.js and Python API.
- Or deploy manually: `vercel --prod`

---

## 9. Making Frontend-Backend Requests

- In your React code, fetch from `/api/your-endpoint` (relative path).
- Example:

  ```typescript
  useEffect(() => {
    fetch("/api/hello")
      .then((res) => res.json())
      .then((data) => setMsg(data.msg));
  }, []);
  ```

---

## 10. Docker: When and Why?

- **Vercel does NOT use your Dockerfile**. It runs Python and Node.js in its own serverless environments.
- **Keep your Dockerfile** for:
  - Local development with containers
  - Deploying to AWS Lambda (container image), ECS, or other platforms that require a custom image
  - Portability to any cloud or on-premise environment
- For Vercel, Dockerfile and .dockerignore are ignored, but are useful for other deployment targets.

---

## 11. Advanced: Authentication, CORS, and Streaming

- For authentication, use JWT or Clerk (this repo: optional Clerk + `CLERK_JWKS_URL` in `backend/api/clerk_auth.py`).
- For CORS, add `CORSMiddleware` in FastAPI (this repo: `backend/api/main.py`, env `CORS_ORIGINS`).
- For streaming (SSE), use FastAPI’s `StreamingResponse` and client-side EventSource or fetch-event-source.

---

## 12. Troubleshooting

- Ensure `vercel.json` routes `/api/*` to your Python backend.
- Delete `/pages/api` if using Python for backend.
- Check Vercel logs for errors.
- Make sure all required env vars are set in Vercel dashboard.

---

## 13. References

- **This repository:** `README.md`, `backend/api/main.py`, `frontend/next.config.ts`, root `Dockerfile`, `.env.example`.
- **Generic examples:** [Vercel FastAPI](https://github.com/vercel/examples/tree/main/python/fastapi), [Next + FastAPI monorepo](https://github.com/vercel/examples/tree/main/python/next-fastapi-monorepo).

---

## 14. Special Considerations for MCP/Agent Deployments on Vercel

Recent updates and documentation from Vercel and FastAPI highlight several nuances and best practices for deploying MCP servers and agent workflows to Vercel:

### 1. Vercel MCP and Agent Resources

- Vercel now provides [dedicated documentation for MCP servers and agent resources](https://vercel.com/docs/mcp) and [AI agent workflows](https://vercel.com/kb/guide/how-to-build-ai-agents-with-vercel-and-the-ai-sdk).
- Use Vercel's [AI SDK](https://vercel.com/docs/ai-sdk) for seamless integration with language models, streaming, and tool calling.
- MCP servers should expose HTTP endpoints (FastAPI/Flask) for agent tool orchestration; stdio-based servers are not supported on Vercel.

### 2. Serverless Function Limits

- Vercel serverless functions have [size and execution time limits](https://vercel.com/docs/functions/usage-and-pricing). Large agent toolchains or long-running workflows may require splitting logic into multiple endpoints or using background jobs (off-platform).
- Avoid large monolithic MCP servers; keep each tool or resource endpoint focused and lightweight.

### 3. Environment Variables and Secrets

- Store all agent keys, model API keys, and MCP secrets in the Vercel dashboard (not in code or .env files).
- Use Vercel's [environment variable management](https://vercel.com/docs/environment-variables) for secure, per-environment configuration.

### 4. Observability and Debugging

- Use Vercel's [Observability suite](https://vercel.com/docs/observability) to monitor agent workflows, MCP tool calls, and serverless function performance.
- For debugging agent/MCP issues, leverage Vercel's logs and, if needed, add custom logging to your FastAPI endpoints.

### 5. Security and Access Control

- Protect agent endpoints and MCP tools with authentication (JWT, Clerk, etc.) as Vercel deployments are public by default.
- Use Vercel's [Deployment Protection](https://vercel.com/docs/deployment-protection) and [RBAC](https://vercel.com/docs/rbac) for access control.

### 6. Tool/Agent Registration

- When deploying agents that dynamically register tools (MCP pattern), ensure all tool registration happens at app startup and is idempotent.
- Avoid runtime code execution or dynamic imports that may not be compatible with Vercel's serverless environment.

### 7. Streaming and Real-Time

- For streaming (SSE, WebSockets), use FastAPI's `StreamingResponse` for HTTP streaming. WebSockets are not natively supported on Vercel serverless, but HTTP streaming works for most agent/LLM use cases.

### 8. Reference Examples

- See [Vercel's official FastAPI example](https://github.com/vercel/examples/tree/main/python/fastapi) and [Next.js + FastAPI monorepo example](https://github.com/vercel/examples/tree/main/python/next-fastapi-monorepo) for up-to-date patterns.
- For MCP/agent-specific patterns, see [Vercel MCP docs](https://vercel.com/docs/mcp) and [AI agent guides](https://vercel.com/kb/ai).

---

**Actionable Changes:**

1. Always expose MCP tools as HTTP endpoints (not stdio) for Vercel compatibility.
2. Split large agent workflows into multiple endpoints/functions to avoid serverless limits.
3. Use Vercel's environment variable dashboard for all secrets and agent config.

---

**With this structure, you can deploy a full-stack app (Next.js frontend + Python MCP/FastAPI backend) to Vercel, with all requests to `/api/*` routed to your MCP backend, and the frontend making requests as needed. Docker is not used by Vercel, but is essential for portability to other platforms.**
