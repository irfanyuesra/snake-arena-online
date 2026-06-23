"""Shared fixtures for the fast unit tests.

These run against a fresh in-memory SQLite database, recreated and reseeded for
every test so they are independent and order-insensitive.
"""

from __future__ import annotations

import os

# Must be set before importing the app so the engine binds to in-memory SQLite.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, create_all, engine
from app.main import app
from app.seed import seed


@pytest.fixture
def client():
    create_all()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
    with TestClient(app) as test_client:
        yield test_client


def auth_token(client: TestClient, username: str = "demo", password: str = "demo") -> str:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token(client)}"}
