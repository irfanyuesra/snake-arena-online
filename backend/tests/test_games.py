"""Tests for the active-game endpoints, including SSE plumbing."""

from __future__ import annotations

import asyncio

from app.events import Broker, games_list_broker
from app.routers.games import _sse
from app.store import store

START_BODY = {
    "mode": "walls",
    "snake": [[10, 10], [9, 10]],
    "food": [3, 4],
    "score": 0,
    "alive": True,
    "width": 20,
    "height": 20,
}


def test_list_active_games_seeded(client):
    resp = client.get("/api/games")
    assert resp.status_code == 200
    games = resp.json()
    assert len(games) == 2
    # Sorted by most recently updated first.
    assert games[0]["updatedAt"] >= games[1]["updatedAt"]


def test_get_unknown_game_is_null(client):
    resp = client.get("/api/games/g_does_not_exist")
    assert resp.status_code == 200
    assert resp.json() is None


def test_start_game_requires_auth(client):
    assert client.post("/api/games", json=START_BODY).status_code == 401


def test_start_game_creates_and_lists(client, auth_headers):
    resp = client.post("/api/games", json=START_BODY, headers=auth_headers)
    assert resp.status_code == 200
    game = resp.json()
    assert game["id"].startswith("g_")
    assert game["userId"] == "u_demo"
    assert game["username"] == "demo"

    fetched = client.get(f"/api/games/{game['id']}")
    assert fetched.json()["id"] == game["id"]


def test_update_game_merges_patch(client, auth_headers):
    game_id = client.post("/api/games", json=START_BODY, headers=auth_headers).json()["id"]

    resp = client.patch(
        f"/api/games/{game_id}", json={"score": 7, "alive": False}, headers=auth_headers
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["score"] == 7
    assert updated["alive"] is False
    # Untouched fields are preserved.
    assert updated["width"] == 20


def test_update_unknown_game_is_404(client, auth_headers):
    resp = client.patch("/api/games/g_nope", json={"score": 1}, headers=auth_headers)
    assert resp.status_code == 404


def test_end_game(client, auth_headers):
    game_id = client.post("/api/games", json=START_BODY, headers=auth_headers).json()["id"]

    assert client.delete(f"/api/games/{game_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/games/{game_id}").json() is None


def test_end_unknown_game_is_404(client, auth_headers):
    assert client.delete("/api/games/g_nope", headers=auth_headers).status_code == 404


def test_sse_event_is_well_formed():
    assert _sse([1, 2]) == "data: [1, 2]\n\n"
    assert _sse(None) == "data: null\n\n"


def test_broker_delivers_payload_to_subscribers():
    async def run():
        broker = Broker()
        queue = broker.subscribe()
        broker.publish({"hello": "world"})
        try:
            return await asyncio.wait_for(queue.get(), 1)
        finally:
            broker.unsubscribe(queue)

    assert asyncio.run(run()) == {"hello": "world"}


def test_notify_list_publishes_active_game_snapshot(client):
    # The /games/stream endpoint relays exactly what notify_list() publishes.
    async def run():
        queue = games_list_broker.subscribe()
        try:
            store.notify_list()
            return await asyncio.wait_for(queue.get(), 1)
        finally:
            games_list_broker.unsubscribe(queue)

    snapshot = asyncio.run(run())
    assert isinstance(snapshot, list)
    assert len(snapshot) == 2
    assert {g["username"] for g in snapshot} == {"demo", "alice"}
