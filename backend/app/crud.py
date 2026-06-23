"""Database operations and ORM-to-Pydantic conversion.

Routers and auth call these helpers with a SQLAlchemy ``Session`` (injected via
``Depends(get_db)``), keeping SQL out of the request handlers.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ActiveGame, GameMode, LeaderboardEntry, User
from .tables import GameRow, LeaderboardRow, RevokedTokenRow, UserRow

# --- converters --------------------------------------------------------


def to_user(row: UserRow) -> User:
    return User(id=row.id, username=row.username)


def to_entry(row: LeaderboardRow) -> LeaderboardEntry:
    return LeaderboardEntry(
        id=row.id,
        userId=row.user_id,
        username=row.username,
        mode=row.mode,  # type: ignore[arg-type]
        score=row.score,
        createdAt=row.created_at,
    )


def to_game(row: GameRow) -> ActiveGame:
    return ActiveGame(
        id=row.id,
        userId=row.user_id,
        username=row.username,
        mode=row.mode,  # type: ignore[arg-type]
        score=row.score,
        snake=[tuple(cell) for cell in row.snake],
        food=tuple(row.food),  # type: ignore[arg-type]
        width=row.width,
        height=row.height,
        alive=row.alive,
        updatedAt=row.updated_at,
    )


# --- users -------------------------------------------------------------


def get_user(db: Session, user_id: str) -> UserRow | None:
    return db.get(UserRow, user_id)


def get_user_by_name(db: Session, username: str) -> UserRow | None:
    stmt = select(UserRow).where(UserRow.username.ilike(username))
    return db.scalars(stmt).first()


def create_user(db: Session, *, id: str, username: str, password_hash: str) -> UserRow:
    row = UserRow(id=id, username=username, password_hash=password_hash)
    db.add(row)
    db.commit()
    return row


# --- leaderboard -------------------------------------------------------


def add_score(
    db: Session, *, id: str, user_id: str, username: str, mode: GameMode,
    score: int, created_at: int,
) -> LeaderboardRow:
    row = LeaderboardRow(
        id=id, user_id=user_id, username=username, mode=mode,
        score=score, created_at=created_at,
    )
    db.add(row)
    db.commit()
    return row


def list_leaderboard(db: Session, mode: GameMode, limit: int) -> list[LeaderboardRow]:
    stmt = (
        select(LeaderboardRow)
        .where(LeaderboardRow.mode == mode)
        .order_by(LeaderboardRow.score.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


# --- games -------------------------------------------------------------


def list_games(db: Session) -> list[GameRow]:
    stmt = select(GameRow).order_by(GameRow.updated_at.desc())
    return list(db.scalars(stmt))


def get_game(db: Session, game_id: str) -> GameRow | None:
    return db.get(GameRow, game_id)


def create_game(db: Session, **fields) -> GameRow:
    row = GameRow(**fields)
    db.add(row)
    db.commit()
    return row


def update_game(db: Session, game_id: str, changes: dict, updated_at: int) -> GameRow | None:
    row = db.get(GameRow, game_id)
    if row is None:
        return None
    for key, value in changes.items():
        setattr(row, key, value)
    row.updated_at = updated_at
    db.commit()
    return row


def delete_game(db: Session, game_id: str) -> bool:
    row = db.get(GameRow, game_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


# --- tokens ------------------------------------------------------------


def revoke_jti(db: Session, jti: str) -> None:
    if db.get(RevokedTokenRow, jti) is None:
        db.add(RevokedTokenRow(jti=jti))
        db.commit()


def is_revoked(db: Session, jti: str) -> bool:
    return db.get(RevokedTokenRow, jti) is not None
