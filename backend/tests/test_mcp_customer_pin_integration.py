"""
Live MCP integration: verify_customer_pin for each fixture row.

Set RUN_MCP_INTEGRATION=1 to enable (hits MCP_SERVER_URL or the default assessment server).
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "meridian_test_customers.json"


def _mcp_url() -> str:
    return (os.environ.get("MCP_SERVER_URL") or "https://order-mcp-74afyau24q-uc.a.run.app/mcp").strip()


def _load_customers() -> list[tuple[str, str]]:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [(str(r["email"]).strip(), str(r["pin"]).strip()) for r in data]


async def _verify_pin(email: str, pin: str) -> str:
    url = _mcp_url()
    async with streamable_http_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "verify_customer_pin",
                {"email": email, "pin": pin},
            )
    if not result.content:
        return ""
    parts: list[str] = []
    for block in result.content:
        if hasattr(block, "text") and block.text:
            parts.append(block.text)
    return "\n".join(parts)


@pytest.mark.integration
@pytest.mark.parametrize("email,pin", _load_customers())
def test_verify_customer_pin_against_live_mcp(email: str, pin: str) -> None:
    if os.environ.get("RUN_MCP_INTEGRATION", "").strip().lower() not in ("1", "true", "yes", "on"):
        pytest.skip("Set RUN_MCP_INTEGRATION=1 to run live MCP customer PIN tests")

    text = asyncio.run(_verify_pin(email, pin))
    lower = text.lower()
    assert "verified" in lower or "customer id" in lower, f"unexpected MCP response for {email!r}:\n{text}"


@pytest.mark.integration
def test_mcp_list_tools_includes_verify_pin() -> None:
    if os.environ.get("RUN_MCP_INTEGRATION", "").strip().lower() not in ("1", "true", "yes", "on"):
        pytest.skip("Set RUN_MCP_INTEGRATION=1 to run live MCP tool discovery test")

    async def _names() -> set[str]:
        url = _mcp_url()
        async with streamable_http_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = await session.list_tools()
        return {t.name for t in listed.tools}

    names = asyncio.run(_names())
    assert "verify_customer_pin" in names
    assert "search_products" in names or "list_products" in names
