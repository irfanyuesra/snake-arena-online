"""Active-game endpoints: list, start, get, update, end, and SSE streams."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import crud
from ..auth import require_user
from ..db import get_db
from ..events import game_item_broker, games_list_broker
from ..models import ActiveGame, StartGameRequest, UpdateGameRequest, User
from ..util import gen_id, now_ms

router = APIRouter(prefix="/games", tags=["Games"])

_KEEPALIVE_SECONDS = 15.0


def _sse(payload: object) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _notify(db: Session, game_id: str) -> None:
    """Publish the new list snapshot and the affected game to SSE subscribers."""
    games_list_broker.publish([crud.to_game(r).model_dump() for r in crud.list_games(db)])
    row = crud.get_game(db, game_id)
    game_item_broker.publish((game_id, crud.to_game(row).model_dump() if row else None))


# --- collection routes (declared before /{id} so "stream" isn't an id) ---


@router.get("", response_model=list[ActiveGame])
async def list_active_games(db: Session = Depends(get_db)) -> list[ActiveGame]:
    return [crud.to_game(row) for row in crud.list_games(db)]


@router.post("", response_model=ActiveGame)
async def start_game(
    body: StartGameRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> ActiveGame:
    row = crud.create_game(
        db,
        id=gen_id("g"),
        user_id=user.id,
        username=user.username,
        mode=body.mode,
        score=body.score,
        snake=[list(cell) for cell in body.snake],
        food=list(body.food),
        width=body.width,
        height=body.height,
        alive=body.alive,
        updated_at=now_ms(),
    )
    _notify(db, row.id)
    return crud.to_game(row)


@router.get("/stream")
async def stream_active_games(request: Request) -> StreamingResponse:
    async def generator() -> AsyncIterator[str]:
        queue = games_list_broker.subscribe()
        try:
            # Initial snapshot uses its own short-lived session.
            from ..db import SessionLocal

            with SessionLocal() as db:
                snapshot = [crud.to_game(r).model_dump() for r in crud.list_games(db)]
            yield _sse(snapshot)
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), _KEEPALIVE_SECONDS)
                    yield _sse(payload)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            games_list_broker.unsubscribe(queue)

    return StreamingResponse(generator(), media_type="text/event-stream")


# --- single-game routes -------------------------------------------------


@router.get("/{id}", response_model=ActiveGame | None)
async def get_active_game(id: str, db: Session = Depends(get_db)) -> ActiveGame | None:
    # Null (not 404) when the game has ended or is unknown — matches the spec.
    row = crud.get_game(db, id)
    return crud.to_game(row) if row else None


@router.patch("/{id}", response_model=ActiveGame)
async def update_game(
    id: str,
    body: UpdateGameRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> ActiveGame:
    changes = body.changes()
    # Cells come in as tuples; store as plain JSON lists.
    if "snake" in changes:
        changes["snake"] = [list(cell) for cell in changes["snake"]]
    if "food" in changes:
        changes["food"] = list(changes["food"])
    row = crud.update_game(db, id, changes, now_ms())
    if row is None:
        raise HTTPException(status_code=404, detail="Game not found")
    _notify(db, id)
    return crud.to_game(row)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_game(
    id: str, user: User = Depends(require_user), db: Session = Depends(get_db)
) -> Response:
    if not crud.delete_game(db, id):
        raise HTTPException(status_code=404, detail="Game not found")
    _notify(db, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}/stream")
async def stream_active_game(id: str, request: Request) -> StreamingResponse:
    async def generator() -> AsyncIterator[str]:
        queue = game_item_broker.subscribe()
        try:
            from ..db import SessionLocal

            with SessionLocal() as db:
                row = crud.get_game(db, id)
                initial = crud.to_game(row).model_dump() if row else None
            yield _sse(initial)
            while True:
                if await request.is_disconnected():
                    break
                try:
                    game_id, payload = await asyncio.wait_for(
                        queue.get(), _KEEPALIVE_SECONDS
                    )
                    if game_id == id:
                        yield _sse(payload)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            game_item_broker.unsubscribe(queue)

    return StreamingResponse(generator(), media_type="text/event-stream")
