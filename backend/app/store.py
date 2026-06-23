"""In-memory data store (no database yet) plus seed data.

A single module-level ``store`` instance holds all state. Call
``store.reset_and_seed()`` to (re)populate it with fake users, scores and
active games — done on app startup and at the start of every test.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

from .events import game_item_broker, games_list_broker
from .models import ActiveGame, LeaderboardEntry


def now_ms() -> int:
    return int(time.time() * 1000)


def _id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(4)}"


@dataclass
class UserRecord:
    id: str
    username: str
    password_hash: str


@dataclass
class Store:
    users: dict[str, UserRecord] = field(default_factory=dict)
    tokens: dict[str, str] = field(default_factory=dict)  # token -> user_id
    leaderboard: list[LeaderboardEntry] = field(default_factory=list)
    games: dict[str, ActiveGame] = field(default_factory=dict)

    # --- lookups -------------------------------------------------------
    def user_by_name(self, username: str) -> UserRecord | None:
        lowered = username.lower()
        for record in self.users.values():
            if record.username.lower() == lowered:
                return record
        return None

    def active_games(self) -> list[ActiveGame]:
        return sorted(self.games.values(), key=lambda g: g.updatedAt, reverse=True)

    # --- SSE notifications --------------------------------------------
    def notify_list(self) -> None:
        games_list_broker.publish([g.model_dump() for g in self.active_games()])

    def notify_game(self, game_id: str) -> None:
        game = self.games.get(game_id)
        game_item_broker.publish((game_id, game.model_dump() if game else None))

    # --- lifecycle -----------------------------------------------------
    def reset(self) -> None:
        self.users.clear()
        self.tokens.clear()
        self.leaderboard.clear()
        self.games.clear()

    def reset_and_seed(self) -> None:
        self.reset()
        _seed(self)


def _seed(store: Store) -> None:
    # Imported lazily to avoid a circular import (auth imports store).
    from .auth import hash_password

    seed_users = [
        UserRecord("u_demo", "demo", hash_password("demo")),
        UserRecord("u_alice", "alice", hash_password("alice")),
        UserRecord("u_bob", "bob", hash_password("bob")),
    ]
    for record in seed_users:
        store.users[record.id] = record

    now = now_ms()
    store.leaderboard.extend(
        [
            LeaderboardEntry(id=_id("lb"), userId="u_alice", username="alice",
                             mode="walls", score=42, createdAt=now - 5000),
            LeaderboardEntry(id=_id("lb"), userId="u_alice", username="alice",
                             mode="wrap", score=67, createdAt=now - 4000),
            LeaderboardEntry(id=_id("lb"), userId="u_demo", username="demo",
                             mode="walls", score=18, createdAt=now - 3000),
            LeaderboardEntry(id=_id("lb"), userId="u_bob", username="bob",
                             mode="wrap", score=55, createdAt=now - 2000),
            LeaderboardEntry(id=_id("lb"), userId="u_bob", username="bob",
                             mode="walls", score=31, createdAt=now - 1000),
        ]
    )

    games = [
        ActiveGame(id=_id("g"), userId="u_demo", username="demo", mode="walls",
                   score=3, snake=[(10, 10), (9, 10), (8, 10)], food=(3, 4),
                   width=20, height=20, alive=True, updatedAt=now - 1500),
        ActiveGame(id=_id("g"), userId="u_alice", username="alice", mode="wrap",
                   score=7, snake=[(5, 5), (5, 6)], food=(12, 8),
                   width=20, height=20, alive=True, updatedAt=now - 500),
    ]
    for game in games:
        store.games[game.id] = game


store = Store()
