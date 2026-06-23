"""Authentication endpoints: signup, login, logout, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import crud
from ..auth import (
    current_token,
    hash_password,
    issue_token,
    optional_user,
    require_user,
    revoke_token,
    verify_password,
)
from ..db import get_db
from ..models import AuthResult, Credentials, User
from ..util import gen_id

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResult)
async def signup(body: Credentials, db: Session = Depends(get_db)) -> AuthResult:
    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if crud.get_user_by_name(db, username) is not None:
        raise HTTPException(status_code=409, detail="Username already taken")

    row = crud.create_user(
        db, id=gen_id("u"), username=username, password_hash=hash_password(body.password)
    )
    token = issue_token(row.id, row.username)
    return AuthResult(user=User(id=row.id, username=row.username), token=token)


@router.post("/login", response_model=AuthResult)
async def login(body: Credentials, db: Session = Depends(get_db)) -> AuthResult:
    row = crud.get_user_by_name(db, body.username.strip())
    if row is None or not verify_password(body.password, row.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = issue_token(row.id, row.username)
    return AuthResult(user=User(id=row.id, username=row.username), token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    _user: User = Depends(require_user),
    token: str | None = Depends(current_token),
    db: Session = Depends(get_db),
) -> Response:
    revoke_token(db, token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=User | None)
async def me(user: User | None = Depends(optional_user)) -> User | None:
    # Missing auth is not an error here — the frontend calls this on startup.
    return user
