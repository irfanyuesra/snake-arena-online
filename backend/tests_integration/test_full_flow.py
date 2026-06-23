"""Full-flow integration tests against an on-disk SQLite database."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_signup_login_submit_and_read_back(client):
    # Sign up
    signup = client.post(
        "/api/auth/signup", json={"username": "itester", "password": "secret"}
    )
    assert signup.status_code == 200, signup.text

    # Log in (separate request → separate auth round-trip)
    login = client.post(
        "/api/auth/login", json={"username": "itester", "password": "secret"}
    )
    assert login.status_code == 200, login.text
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Submit a score
    submit = client.post(
        "/api/leaderboard/scores",
        json={"mode": "walls", "score": 77},
        headers=headers,
    )
    assert submit.status_code == 200, submit.text

    # Read it back from the leaderboard
    board = client.get("/api/leaderboard", params={"mode": "walls", "limit": 100})
    assert board.status_code == 200
    mine = [e for e in board.json() if e["username"] == "itester"]
    assert len(mine) == 1
    assert mine[0]["score"] == 77


def test_score_persists_across_connections(client):
    token = client.post(
        "/api/auth/login", json={"username": "demo", "password": "demo"}
    ).json()["token"]
    client.post(
        "/api/leaderboard/scores",
        json={"mode": "wrap", "score": 4242},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Drop all pooled connections, then read with a brand-new client. The data
    # is only available if it was actually written to the file on disk.
    from app.db import engine

    engine.dispose()

    with TestClient(app) as fresh_client:
        board = fresh_client.get("/api/leaderboard", params={"mode": "wrap", "limit": 100})
        assert any(e["score"] == 4242 for e in board.json())
