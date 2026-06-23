"""Password hashing and bearer-token authentication.

Passwords are hashed with PBKDF2-HMAC-SHA256 from the standard library, so
there are no native build dependencies (bcrypt/argon2) to install on Windows.
Tokens are opaque, generated with ``secrets`` and kept in the in-memory store.
"""

from __future__ import annotations

import hashlib
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import User
from .store import store

_ITERATIONS = 100_000
# auto_error=False so we can return a friendly 401 / allow optional auth.
_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str, salt: str | None = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _ITERATIONS
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(stored, hash_password(password, salt))


def issue_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    store.tokens[token] = user_id
    return token


def revoke_token(token: str) -> None:
    store.tokens.pop(token, None)


def _user_from_token(token: str | None) -> User | None:
    if not token:
        return None
    user_id = store.tokens.get(token)
    if user_id is None:
        return None
    record = store.users.get(user_id)
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
