"""Verify Clerk session JWTs (Bearer) when CLERK_JWKS_URL is configured."""

from __future__ import annotations

import logging
import os
from functools import lru_cache

import jwt
from fastapi import Header, HTTPException
from jwt import PyJWKClient

logger = logging.getLogger(__name__)


def clerk_auth_enabled() -> bool:
    return bool((os.environ.get("CLERK_JWKS_URL") or "").strip())


def clerk_auth_strict() -> bool:
    """When True with CLERK_JWKS_URL set, always require Bearer (even on Hugging Face Spaces)."""
    v = (os.environ.get("CLERK_AUTH_STRICT") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def huggingface_space_runtime() -> bool:
    """True when Hugging Face Spaces injects its runtime env (Docker Space). Not all builds expose SPACE_ID."""
    for key in (
        "SPACE_ID",
        "SPACE_REPO_NAME",
        "SPACE_AUTHOR_NAME",
        "SPACE_HOST",
        "SPACE_TITLE",
    ):
        if (os.environ.get(key) or "").strip():
            return True
    return False


def clerk_auth_optional() -> bool:
    """When True with CLERK_JWKS_URL set, missing Bearer is treated as anonymous (HF same-origin UI)."""
    if clerk_auth_strict():
        return False
    # On HF, bundled docker-hf UI never sends Clerk; Vercel clients can still send Bearer (verified when present).
    if huggingface_space_runtime():
        return True
    v = (os.environ.get("CLERK_AUTH_OPTIONAL") or "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return False


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    url = (os.environ.get("CLERK_JWKS_URL") or "").strip()
    if not url:
        raise RuntimeError("CLERK_JWKS_URL is not set")
    return PyJWKClient(url)


def verify_clerk_bearer_token(token: str) -> str:
    """Validate Clerk session JWT and return the subject (Clerk user id)."""
    token = token.strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        issuer = (os.environ.get("CLERK_ISSUER") or "").strip() or None
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as e:
        logger.info("clerk jwt verify failed: %s", e)
        raise HTTPException(status_code=401, detail="Invalid or expired session") from e
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return sub


async def resolve_clerk_user_id(
    authorization: str | None = Header(None, alias="Authorization"),
) -> str | None:
    """If Clerk is configured, validate Bearer when present; optional mode allows no Bearer (anonymous)."""
    if not clerk_auth_enabled():
        return None
    auth_lower = (authorization or "").lower()
    if not authorization or not auth_lower.startswith("bearer "):
        if clerk_auth_optional():
            return None
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <clerk_session_jwt> required",
        )
    raw = authorization[7:].strip()
    # Clerk can send "Bearer " with no token during transitions; treat like missing when anonymous is allowed.
    if not raw and clerk_auth_optional():
        return None
    if not raw:
        raise HTTPException(status_code=401, detail="Authorization bearer token required")
    return verify_clerk_bearer_token(raw)
