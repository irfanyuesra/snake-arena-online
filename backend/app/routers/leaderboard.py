"""Leaderboard endpoints: list entries and submit a finished score."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..auth import require_user
from ..models import GameMode, LeaderboardEntry, SubmitScoreRequest, User
from ..store import _id, now_ms, store

router = APIRouter(tags=["Leaderboard"])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    mode: GameMode,
    limit: int = Query(default=10, ge=1, le=100),
) -> list[LeaderboardEntry]:
    entries = [e for e in store.leaderboard if e.mode == mode]
    entries.sort(key=lambda e: e.score, reverse=True)
    return entries[:limit]


@router.post("/leaderboard/scores", response_model=LeaderboardEntry)
async def submit_score(
    body: SubmitScoreRequest, user: User = Depends(require_user)
) -> LeaderboardEntry:
    entry = LeaderboardEntry(
        id=_id("lb"),
        userId=user.id,
        username=user.username,
        mode=body.mode,
        score=body.score,
        createdAt=now_ms(),
    )
    store.leaderboard.append(entry)
    return entry
