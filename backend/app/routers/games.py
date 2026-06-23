"""Active-game endpoints: list, start, get, update, end, and SSE streams."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse

from ..auth import require_user
from ..events import game_item_broker, games_list_broker
from ..models import ActiveGame, StartGameRequest, UpdateGameRequest, User
from ..store import _id, now_ms, store

router = APIRouter(prefix="/games", tags=["Games"])

_KEEPALIVE_SECONDS = 15.0


def _sse(payload: object) -> str:
    return f"data: {json.dumps(payload)}\n\n"


# --- collection routes (declared before /{id} so "stream" isn't an id) ---


@router.get("", response_model=list[ActiveGame])
async def list_active_games() -> list[ActiveGame]:
    return store.active_games()


@router.post("", response_model=ActiveGame)
async def start_game(
    body: StartGameRequest, user: User = Depends(require_user)
) -> ActiveGame:
    game = ActiveGame(
        id=_id("g"),
        userId=user.id,
        username=user.username,
        mode=body.mode,
        score=body.score,
        snake=body.snake,
        food=body.food,
        width=body.width,
        height=body.height,
        alive=body.alive,
        updatedAt=now_ms(),
    )
    store.games[game.id] = game
    store.notify_list()
    store.notify_game(game.id)
    return game


@router.get("/stream")
async def stream_active_games(request: Request) -> StreamingResponse:
    async def generator() -> AsyncIterator[str]:
        queue = games_list_broker.subscribe()
        try:
            yield _sse([g.model_dump() for g in store.active_games()])
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
async def get_active_game(id: str) -> ActiveGame | None:
    # Null (not 404) when the game has ended or is unknown — matches the spec.
    return store.games.get(id)


@router.patch("/{id}", response_model=ActiveGame)
async def update_game(
    id: str, body: UpdateGameRequest, user: User = Depends(require_user)
) -> ActiveGame:
    game = store.games.get(id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    updated = game.model_copy(update={**body.changes(), "updatedAt": now_ms()})
    store.games[id] = updated
    store.notify_list()
    store.notify_game(id)
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def end_game(id: str, user: User = Depends(require_user)) -> Response:
    if store.games.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="Game not found")
    store.notify_list()
    store.notify_game(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}/stream")
async def stream_active_game(id: str, request: Request) -> StreamingResponse:
    async def generator() -> AsyncIterator[str]:
        queue = game_item_broker.subscribe()
        try:
            current = store.games.get(id)
            yield _sse(current.model_dump() if current else None)
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
