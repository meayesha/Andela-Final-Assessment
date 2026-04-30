"""FastAPI app: MCP-backed todo agent with streaming, session history, and todo API."""

from __future__ import annotations

import json
import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Repo root (parent of backend/) — single .env lives here
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(REPO_ROOT / ".env")

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel, Field

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from agents.memory import SQLiteSession

from api.clerk_auth import clerk_auth_enabled, resolve_clerk_user_id
from api.history_util import session_items_to_chat
from api.openrouter import build_openrouter_run_config, openrouter_model_name
from todo_mcp.store import list_todos_for_api

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent


def _env_nonempty(key: str, default: str) -> str:
    """Treat empty or whitespace env as unset (`.env` often has `KEY=` placeholders)."""
    raw = os.environ.get(key)
    if raw is None:
        return default
    stripped = str(raw).strip()
    return stripped if stripped else default


DATA_DIR = Path(_env_nonempty("DATA_DIR", str(BACKEND_ROOT / "data"))).resolve()
TODO_DB_PATH = Path(_env_nonempty("TODO_DB_PATH", str(DATA_DIR / "todos.db"))).resolve()
AGENT_DB_PATH = Path(_env_nonempty("AGENT_DB_PATH", str(DATA_DIR / "agent_sessions.sqlite"))).resolve()

if not (os.environ.get("TODO_DB_PATH") or "").strip():
    os.environ["TODO_DB_PATH"] = str(TODO_DB_PATH)

DATA_DIR.mkdir(parents=True, exist_ok=True)
TODO_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
AGENT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

OPENROUTER_RUN_CONFIG = build_openrouter_run_config()

INSTRUCTIONS = """You are a concise todo assistant. You only help with the user's todo list using the provided tools (create, list, update, delete, set completed).

Scope and refusals:
- If the user asks for anything outside todos (e.g. stock prices, news, general knowledge, coding, health, legal, or other topics), reply briefly that you can only assist with todos. Do not browse the web, you have no internet access, and you cannot provide real-time or external data.
- Do not recommend websites, apps, brokerages, news outlets, or "where to look" for off-topic requests. No lists of links or brands. After declining, you may offer to help with their todos only.

Todo behavior:
- Interpret natural language and call the right tools.
- After tool calls, summarize results clearly.
- If an id does not exist, say so and suggest listing todos."""


class ChatStreamBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: str = Field(..., min_length=8, max_length=128)


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _chat_event_stream(body: ChatStreamBody, clerk_user_id: str | None) -> AsyncIterator[str]:
    todo_uid = clerk_user_id if clerk_user_id is not None else ""
    effective_session = clerk_user_id if clerk_user_id is not None else body.session_id

    mcp = MCPServerStdio(
        name="todo-mcp",
        params={
            "command": sys.executable,
            "args": ["-m", "todo_mcp"],
            "cwd": str(BACKEND_ROOT),
            "env": {
                **os.environ,
                "PYTHONPATH": str(BACKEND_ROOT),
                "TODO_DB_PATH": str(TODO_DB_PATH),
                "TODO_USER_ID": todo_uid,
            },
        },
        cache_tools_list=True,
    )
    async with mcp:
        agent = Agent(
            name="Todo Assistant",
            instructions=INSTRUCTIONS,
            model=openrouter_model_name(),
            mcp_servers=[mcp],
        )
        session = SQLiteSession(effective_session, db_path=AGENT_DB_PATH)
        result = Runner.run_streamed(
            agent,
            input=body.message.strip(),
            session=session,
            run_config=OPENROUTER_RUN_CONFIG,
        )
        try:
            async for event in result.stream_events():
                if event.type != "raw_response_event":
                    continue
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent):
                    delta = data.delta
                    if delta:
                        yield _sse({"type": "token", "text": delta})
            yield _sse({"type": "done"})
        except Exception as e:
            logger.exception("stream failed")
            yield _sse({"type": "error", "message": str(e)})


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not (os.environ.get("OPENROUTER_API_KEY") or "").strip():
        logger.warning("OPENROUTER_API_KEY is not set; chat will fail until it is configured.")
    if clerk_auth_enabled():
        logger.info("Clerk JWT verification enabled (CLERK_JWKS_URL).")
    yield


app = FastAPI(title="Todo MCP Chat API", lifespan=lifespan)


def _cors_allow_origins() -> list[str]:
    """Parse CORS_ORIGINS. Empty env (common in .env) must not become [\"\"] — that blocks every origin."""
    raw = (os.environ.get("CORS_ORIGINS") or "").strip()
    if not raw:
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ]
    return [o.strip() for o in raw.split(",") if o.strip()]


def _cors_allow_origin_regex() -> str | None:
    """When using built-in dev origins, also allow LAN URLs (e.g. Next.js Network http://192.168.x.x:3000)."""
    if (os.environ.get("CORS_ORIGINS") or "").strip():
        return None
    # http(s) + localhost / loopback / typical RFC1918 LAN + any port (dev servers)
    return (
        r"^https?://("
        r"localhost|127\.0\.0\.1|"
        r"192\.168\.\d{1,3}\.\d{1,3}|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        r"):\d+$"
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_origin_regex=_cors_allow_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat/stream")
async def chat_stream(
    body: ChatStreamBody,
    clerk_user_id: str | None = Depends(resolve_clerk_user_id),
):
    return StreamingResponse(
        _chat_event_stream(body, clerk_user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/todos")
async def get_todos(clerk_user_id: str | None = Depends(resolve_clerk_user_id)):
    return list_todos_for_api(clerk_user_id or "")


@app.get("/api/session/{session_id}/history")
async def get_history(
    session_id: str,
    clerk_user_id: str | None = Depends(resolve_clerk_user_id),
):
    if len(session_id) < 8 or len(session_id) > 128:
        raise HTTPException(400, "invalid session_id")
    if clerk_user_id is not None and session_id != clerk_user_id:
        raise HTTPException(403, "session_id must match the signed-in user")
    effective = clerk_user_id if clerk_user_id is not None else session_id
    session = SQLiteSession(effective, db_path=AGENT_DB_PATH)
    items = await session.get_items()
    if not items:
        return {"messages": []}
    normalized: list[dict[str, Any]] = []
    for i in items:
        if isinstance(i, dict):
            normalized.append(i)
        elif hasattr(i, "model_dump"):
            normalized.append(i.model_dump())  # type: ignore[union-attr]
        else:
            normalized.append(dict(i))  # type: ignore[arg-type]
    return {"messages": session_items_to_chat(normalized)}


@app.get("/api/health")
async def health():
    return {
        "ok": True,
        "todo_db": str(TODO_DB_PATH),
        "agent_db": str(AGENT_DB_PATH),
        "llm": "openrouter",
        "model": openrouter_model_name(),
        "clerk_auth": clerk_auth_enabled(),
    }


_STATIC = BACKEND_ROOT / "static"
if _STATIC.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(_STATIC), html=True), name="static")
