"""Tests for the leaderboard endpoints."""

from __future__ import annotations


def test_leaderboard_filtered_and_sorted_desc(client):
    resp = client.get("/api/leaderboard", params={"mode": "walls"})
    assert resp.status_code == 200
    entries = resp.json()
    assert entries, "expected seeded walls entries"
    assert all(e["mode"] == "walls" for e in entries)
    scores = [e["score"] for e in entries]
    assert scores == sorted(scores, reverse=True)


def test_leaderboard_respects_limit(client):
    resp = client.get("/api/leaderboard", params={"mode": "walls", "limit": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_leaderboard_requires_mode(client):
    resp = client.get("/api/leaderboard")
    assert resp.status_code == 400


def test_submit_score_requires_auth(client):
    resp = client.post("/api/leaderboard/scores", json={"mode": "walls", "score": 5})
    assert resp.status_code == 401


def test_submit_score_persists_entry(client, auth_headers):
    resp = client.post(
        "/api/leaderboard/scores",
        json={"mode": "wrap", "score": 99},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    entry = resp.json()
    assert entry["score"] == 99
    assert entry["username"] == "demo"
    assert entry["id"].startswith("lb_")

    top = client.get("/api/leaderboard", params={"mode": "wrap", "limit": 1}).json()
    assert top[0]["score"] == 99


def test_submit_score_rejects_negative(client, auth_headers):
    resp = client.post(
        "/api/leaderboard/scores",
        json={"mode": "walls", "score": -1},
        headers=auth_headers,
    )
    assert resp.status_code == 400
