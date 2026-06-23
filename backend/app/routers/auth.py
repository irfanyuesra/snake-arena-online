"""Authentication endpoints: signup, login, logout, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..auth import (
    current_token,
    hash_password,
    issue_token,
    optional_user,
    require_user,
    revoke_token,
    verify_password,
)
from ..models import AuthResult, Credentials, User
from ..store import UserRecord, _id, store

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResult)
async def signup(body: Credentials) -> AuthResult:
    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if store.user_by_name(username) is not None:
        raise HTTPException(status_code=409, detail="Username already taken")

    record = UserRecord(
        id=_id("u"), username=username, password_hash=hash_password(body.password)
    )
    store.users[record.id] = record
    token = issue_token(record.id)
    return AuthResult(user=User(id=record.id, username=record.username), token=token)


@router.post("/login", response_model=AuthResult)
async def login(body: Credentials) -> AuthResult:
    record = store.user_by_name(body.username.strip())
    if record is None or not verify_password(body.password, record.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = issue_token(record.id)
    return AuthResult(user=User(id=record.id, username=record.username), token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    _user: User = Depends(require_user), token: str | None = Depends(current_token)
) -> Response:
    if token:
        revoke_token(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=User | None)
async def me(user: User | None = Depends(optional_user)) -> User | None:
    # Missing auth is not an error here — the frontend calls this on startup.
    return user
