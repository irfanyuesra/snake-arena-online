"""Database engine and session, configured from ``DATABASE_URL``.

The URL alone selects the backend, so the same code runs on SQLite locally and
Postgres later without changes. Examples:

    sqlite:///./snake.db
    postgresql+psycopg://user:pass@localhost:5432/snake_arena
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Load backend/.env if present. override=False so an explicitly-set
# DATABASE_URL (e.g. in tests) always wins over the file.
load_dotenv(override=False)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./snake.db")

_is_sqlite = DATABASE_URL.startswith("sqlite")
_is_memory = DATABASE_URL in ("sqlite://", "sqlite:///:memory:")

_connect_args = {"check_same_thread": False} if _is_sqlite else {}
_engine_kwargs: dict = {"future": True, "connect_args": _connect_args}
if _is_memory:
    # Keep one shared connection so the in-memory DB survives across sessions.
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    pass


def create_all() -> None:
    # Import models so they register on Base before creating tables.
    from . import tables  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
