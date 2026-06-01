from __future__ import annotations


def test_login_success(client):
    resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin123456"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["username"] == "admin"
    assert "project:create" in body["data"]["user"]["permission_codes"]


def test_login_wrong_password(client):
    resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_current_user(client, admin_token):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == "admin"
