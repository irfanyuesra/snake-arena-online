"""Leaderboard endpoints: list entries and submit a finished score."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud
from ..auth import require_user
from ..db import get_db
from ..models import GameMode, LeaderboardEntry, SubmitScoreRequest, User
from ..util import gen_id, now_ms

router = APIRouter(tags=["Leaderboard"])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    mode: GameMode,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[LeaderboardEntry]:
    rows = crud.list_leaderboard(db, mode, limit)
    return [crud.to_entry(row) for row in rows]


@router.post("/leaderboard/scores", response_model=LeaderboardEntry)
async def submit_score(
    body: SubmitScoreRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> LeaderboardEntry:
    row = crud.add_score(
        db,
        id=gen_id("lb"),
        user_id=user.id,
        username=user.username,
        mode=body.mode,
        score=body.score,
        created_at=now_ms(),
    )
    return crud.to_entry(row)
