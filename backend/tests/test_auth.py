"""Tests for the auth endpoints."""

from __future__ import annotations


def test_signup_creates_account_and_returns_token(client):
    resp = client.post("/api/auth/signup", json={"username": "carol", "password": "pw"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["username"] == "carol"
    assert body["user"]["id"].startswith("u_")
    assert body["token"]


def test_signup_duplicate_username_conflicts(client):
    resp = client.post("/api/auth/signup", json={"username": "demo", "password": "x"})
    assert resp.status_code == 409
    assert resp.json() == {"message": "Username already taken"}


def test_signup_blank_username_is_bad_request(client):
    resp = client.post("/api/auth/signup", json={"username": "   ", "password": "x"})
    assert resp.status_code == 400
    assert "message" in resp.json()


def test_login_succeeds_with_seeded_credentials(client):
    resp = client.post("/api/auth/login", json={"username": "demo", "password": "demo"})
    assert resp.status_code == 200
    assert resp.json()["user"]["id"] == "u_demo"


def test_login_rejects_wrong_password(client):
    resp = client.post("/api/auth/login", json={"username": "demo", "password": "nope"})
    assert resp.status_code == 401
    assert resp.json() == {"message": "Invalid credentials"}


def test_me_is_null_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json() is None


def test_me_returns_user_with_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "demo"


def test_logout_invalidates_token(client):
    token = client.post(
        "/api/auth/login", json={"username": "demo", "password": "demo"}
    ).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    # The token no longer authenticates.
    assert client.get("/api/auth/me", headers=headers).json() is None


def test_logout_requires_auth(client):
    assert client.post("/api/auth/logout").status_code == 401
