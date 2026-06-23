"""SQLAlchemy ORM models (database tables).

Snake/food cells are stored as JSON arrays, which works on both SQLite and
Postgres via SQLAlchemy's generic JSON type.
"""

from __future__ import annotations

from sqlalchemy import JSON, BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)


class LeaderboardRow(Base):
    __tablename__ = "leaderboard"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    username: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String, index=True)
    score: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger)


class GameRow(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    username: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    score: Mapped[int] = mapped_column(Integer)
    snake: Mapped[list] = mapped_column(JSON)
    food: Mapped[list] = mapped_column(JSON)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    alive: Mapped[bool] = mapped_column(Boolean)
    updated_at: Mapped[int] = mapped_column(BigInteger)


class RevokedTokenRow(Base):
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String, primary_key=True)
