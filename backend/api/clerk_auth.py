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
    """If Clerk is configured, require a valid Bearer token and return user id; else None."""
    if not clerk_auth_enabled():
        return None
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization: Bearer <clerk_session_jwt> required",
        )
    raw = authorization[7:].strip()
    return verify_clerk_bearer_token(raw)
