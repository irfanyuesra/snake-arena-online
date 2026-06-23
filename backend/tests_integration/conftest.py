"""Integration-test fixtures.

These run against a real SQLite file on disk (not in-memory), so they exercise
persistence across separate database connections — the thing an in-memory store
could never prove.
"""

from __future__ import annotations

import os
import pathlib
import tempfile

# Point the app at a fresh on-disk SQLite file before importing it.
_tmp_dir = tempfile.mkdtemp(prefix="snake_itest_")
_db_path = pathlib.Path(_tmp_dir) / "snake.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path.as_posix()}"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    # Lifespan creates the tables and seeds on first start.
    with TestClient(app) as test_client:
        yield test_client
