"""Seed the database with fake users, scores, and active games.

Only runs when the users table is empty, so it is safe to call on every
startup without clobbering persisted data.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import hash_password
from .tables import GameRow, LeaderboardRow, UserRow
from .util import gen_id, now_ms


def seed_if_empty(db: Session) -> None:
    count = db.scalar(select(func.count()).select_from(UserRow))
    if count:
        return
    seed(db)


def seed(db: Session) -> None:
    users = [
        UserRow(id="u_demo", username="demo", password_hash=hash_password("demo")),
        UserRow(id="u_alice", username="alice", password_hash=hash_password("alice")),
        UserRow(id="u_bob", username="bob", password_hash=hash_password("bob")),
    ]
    db.add_all(users)

    now = now_ms()
    db.add_all(
        [
            LeaderboardRow(id=gen_id("lb"), user_id="u_alice", username="alice",
                           mode="walls", score=42, created_at=now - 5000),
            LeaderboardRow(id=gen_id("lb"), user_id="u_alice", username="alice",
                           mode="wrap", score=67, created_at=now - 4000),
            LeaderboardRow(id=gen_id("lb"), user_id="u_demo", username="demo",
                           mode="walls", score=18, created_at=now - 3000),
            LeaderboardRow(id=gen_id("lb"), user_id="u_bob", username="bob",
                           mode="wrap", score=55, created_at=now - 2000),
            LeaderboardRow(id=gen_id("lb"), user_id="u_bob", username="bob",
                           mode="walls", score=31, created_at=now - 1000),
        ]
    )

    db.add_all(
        [
            GameRow(id=gen_id("g"), user_id="u_demo", username="demo", mode="walls",
                    score=3, snake=[[10, 10], [9, 10], [8, 10]], food=[3, 4],
                    width=20, height=20, alive=True, updated_at=now - 1500),
            GameRow(id=gen_id("g"), user_id="u_alice", username="alice", mode="wrap",
                    score=7, snake=[[5, 5], [5, 6]], food=[12, 8],
                    width=20, height=20, alive=True, updated_at=now - 500),
        ]
    )
    db.commit()
