from __future__ import annotations

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import session as db_session
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.seed.seed_data import seed_all

# In-memory SQLite for fast isolated tests.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _override_dependencies():
    app.dependency_overrides[get_db] = _override_get_db
    # Prevent the startup lifespan from touching the real database.
    db_session.SessionLocal = TestingSessionLocal
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def _login(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["access_token"]


@pytest.fixture
def admin_token(client):
    return _login(client, "admin", "Admin123456")


@pytest.fixture
def staff_token(client):
    return _login(client, "staff", "Staff123456")
