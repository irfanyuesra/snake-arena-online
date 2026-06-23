"""Password hashing and JWT bearer-token authentication.

Passwords are hashed with PBKDF2-HMAC-SHA256 from the standard library (no
native build dependencies). Bearer tokens are signed JWTs (HS256). Logout adds
the token's ``jti`` to an in-memory deny-list so it stops authenticating.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import time

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import User
from .store import store

_PBKDF2_ITERATIONS = 100_000

_JWT_ALGORITHM = "HS256"
# Set SNAKE_JWT_SECRET in production. In dev we fall back to a per-process
# random secret (tokens become invalid across restarts, which is fine locally).
_JWT_SECRET = os.environ.get("SNAKE_JWT_SECRET") or secrets.token_urlsafe(32)
_TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

# auto_error=False so we can return a friendly 401 / allow optional auth.
_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str, salt: str | None = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(stored, hash_password(password, salt))


def issue_token(user_id: str, username: str) -> str:
    now = int(time.time())
    payload = {
        "sub": user_id,
        "username": username,
        "iat": now,
        "exp": now + _TOKEN_TTL_SECONDS,
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


def _decode(token: str) -> dict | None:
    try:
        return jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def revoke_token(token: str | None) -> None:
    if not token:
        return
    payload = _decode(token)
    if payload and payload.get("jti"):
        store.revoked.add(payload["jti"])


def _user_from_token(token: str | None) -> User | None:
    if not token:
        return None
    payload = _decode(token)
    if not payload or payload.get("jti") in store.revoked:
        return None
    record = store.users.get(payload.get("sub", ""))
    return User(id=record.id, username=record.username) if record else None


async def optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User | None:
    """Current user when a valid token is present, otherwise ``None``."""
    return _user_from_token(creds.credentials if creds else None)


async def require_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User:
    """Current user, or 401 when authentication is missing/invalid."""
    user = _user_from_token(creds.credentials if creds else None)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def current_token(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str | None:
    return creds.credentials if creds else None
