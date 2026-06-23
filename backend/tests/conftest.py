"""Shared test fixtures.

Each test gets a fresh TestClient whose lifespan re-seeds the in-memory store,
so tests are independent and order-insensitive.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def auth_token(client: TestClient, username: str = "demo", password: str = "demo") -> str:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_token(client)}"}
