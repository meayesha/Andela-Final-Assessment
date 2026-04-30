"""Smoke tests for the public health endpoint (no external MCP or LLM calls)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_ok_and_mcp_metadata() -> None:
    from api.main import app

    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["mcp_transport"] == "streamable-http"
    assert body["mcp_server_host"]
    assert isinstance(body["mcp_server_host"], str)
    assert body["model"]
    assert "agent_db" in body
