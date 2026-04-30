"""OpenRouter: OpenAI-compatible client + Chat Completions (not Responses API)."""

from __future__ import annotations

import os

from openai import AsyncOpenAI, DefaultAsyncHttpxClient

from agents.models.openai_provider import OpenAIProvider
from agents.run_config import RunConfig

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-mini"


def openrouter_model_name() -> str:
    return (os.environ.get("OPENROUTER_MODEL") or DEFAULT_MODEL).strip()


def build_openrouter_run_config() -> RunConfig:
    api_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
    base_url = (os.environ.get("OPENROUTER_BASE_URL") or DEFAULT_BASE_URL).strip()

    headers: dict[str, str] = {}
    referer = (os.environ.get("OPENROUTER_HTTP_REFERER") or "").strip()
    title = (os.environ.get("OPENROUTER_APP_TITLE") or "Meridian Support Chat").strip()
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title

    client = AsyncOpenAI(
        api_key=api_key or "missing-openrouter-api-key",
        base_url=base_url,
        default_headers=headers or None,
        http_client=DefaultAsyncHttpxClient(),
    )
    provider = OpenAIProvider(
        openai_client=client,
        use_responses=False,
    )
    return RunConfig(
        model_provider=provider,
        tracing_disabled=True,
    )
