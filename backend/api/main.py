"""FastAPI app: Meridian support agent with remote MCP (Streamable HTTP), streaming, session history."""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(REPO_ROOT / ".env")

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel, Field

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.memory import SQLiteSession

from api.clerk_auth import (
    clerk_auth_enabled,
    clerk_auth_optional,
    clerk_auth_strict,
    huggingface_space_runtime,
    resolve_clerk_user_id,
)
from api.history_util import session_items_to_chat
from api.openrouter import build_openrouter_run_config, openrouter_model_name

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MCP_SERVER_URL = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"


def _env_nonempty(key: str, default: str) -> str:
    raw = os.environ.get(key)
    if raw is None:
        return default
    stripped = str(raw).strip()
    return stripped if stripped else default


DATA_DIR = Path(_env_nonempty("DATA_DIR", str(BACKEND_ROOT / "data"))).resolve()
AGENT_DB_PATH = Path(_env_nonempty("AGENT_DB_PATH", str(DATA_DIR / "agent_sessions.sqlite"))).resolve()

DATA_DIR.mkdir(parents=True, exist_ok=True)
AGENT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

OPENROUTER_RUN_CONFIG = build_openrouter_run_config()

INSTRUCTIONS = """You are the Meridian Electronics customer support assistant. Meridian sells computer products: monitors, keyboards, printers, networking gear, and accessories.

You have tools from Meridian's internal order system (MCP). Use them to help customers in a professional, friendly way.

Capabilities (use tools when relevant):
- **Products:** Search or list products; get details by SKU for availability, specs, and descriptions.
- **Customers:** Look up a customer by ID when they provide it. Use **verify_customer_pin** when they give an email and a 4-digit PIN to confirm identity before sharing sensitive order details or placing orders.
- **Orders:** List orders (optionally filter by customer or status), get order details by ID, create new orders with line items when the customer is verified and has provided a clear cart (SKUs + quantities).

Guidelines:
- Never invent SKUs, prices, order IDs, or customer UUIDs. Prefer tool results.
- If the customer is vague, ask concise clarifying questions.
- For cancellations, returns, or anything your tools cannot do, explain the limit and suggest contacting human support.
- Keep answers concise unless the user asks for detail. Summarize tool output clearly.
- Do not claim to browse the general web or offer real-time data you cannot verify from Meridian systems.
- Report catalog fields exactly as returned (including descriptions). Do not apologize for, judge, or call out "unclear" or odd-looking product text unless the customer explicitly asks about description quality.

Scope (customer-facing wording):
- You only help with Meridian Electronics: products, availability, orders, and account verification. For anything else (e.g. stock market, news, unrelated tech, homework, medical/legal advice), reply in one short sentence: you can only provide information about Meridian Electronics and its products, and invite them to ask about those topics.
- Never tell the customer you "only have access to tools," "internal tools," "MCP," or similar—keep refusals plain and professional."""


class ChatStreamBody(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: str = Field(..., min_length=8, max_length=128)


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _mcp_server_url() -> str:
    return (os.environ.get("MCP_SERVER_URL") or DEFAULT_MCP_SERVER_URL).strip()


def _mcp_url_host() -> str:
    try:
        return urlparse(_mcp_server_url()).netloc or "unset"
    except Exception:
        return "invalid-url"


async def _chat_event_stream(body: ChatStreamBody, clerk_user_id: str | None) -> AsyncIterator[str]:
    effective_session = clerk_user_id if clerk_user_id is not None else body.session_id
    mcp_url = _mcp_server_url()

    mcp = MCPServerStreamableHttp(
        params={
            "url": mcp_url,
            "timeout": timedelta(seconds=60),
            "sse_read_timeout": timedelta(seconds=300),
        },
        cache_tools_list=True,
        name="meridian-orders",
        client_session_timeout_seconds=120,
    )
    async with mcp:
        agent = Agent(
            name="Meridian Support",
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
    logger.info("MCP server host: %s (transport: streamable-http)", _mcp_url_host())
    if clerk_auth_enabled():
        if clerk_auth_optional():
            logger.info(
                "Clerk JWT enabled; missing Bearer uses anonymous session "
                "(default on Hugging Face when SPACE_ID is set, or set CLERK_AUTH_OPTIONAL=1). "
                "Bearer is still verified when sent.",
            )
        else:
            logger.info("Clerk JWT verification enabled (CLERK_JWKS_URL); Bearer required on API routes.")
    yield


app = FastAPI(title="Meridian Support Chat API", lifespan=lifespan)


def _cors_allow_origins() -> list[str]:
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
    if (os.environ.get("CORS_ORIGINS") or "").strip():
        return None
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
@app.post("/api/chat/stream/")
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


@app.get("/api/session/{session_id}/history")
@app.get("/api/session/{session_id}/history/")
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
        "agent_db": str(AGENT_DB_PATH),
        "llm": "openrouter",
        "model": openrouter_model_name(),
        "mcp_transport": "streamable-http",
        "mcp_server_host": _mcp_url_host(),
        "clerk_auth": clerk_auth_enabled(),
        "clerk_auth_optional": clerk_auth_optional(),
        "clerk_auth_strict": clerk_auth_strict(),
        "huggingface_space_runtime": huggingface_space_runtime(),
        "space_id_set": bool((os.environ.get("SPACE_ID") or "").strip()),
    }


_STATIC = BACKEND_ROOT / "static"
if _STATIC.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/", StaticFiles(directory=str(_STATIC), html=True), name="static")
