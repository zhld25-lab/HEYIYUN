"""Tests for Phase 4A workflow engine."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _login(client: TestClient, username: str, password: str) -> str:
    r = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["data"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Test: create workflow (PM role has workflow:create)
# ---------------------------------------------------------------------------

def test_create_and_get_workflow(client: TestClient):
    token = _login(client, "pm", "PM123456")
    # Get the first project id
    r = client.get("/api/v1/projects", headers=_auth(token))
    project_id = r.json()["data"]["items"][0]["id"]

    r = client.post(
        "/api/v1/workflows",
        json={
            "business_type": "project",
            "business_id": project_id,
            "project_id": project_id,
            "title": f"项目立项审批测试",
            "workflow_type": "项目立项审批",
        },
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text
    wf = r.json()["data"]
    assert wf["status"] == "draft"
    assert wf["total_steps"] == 3
    assert len(wf["steps"]) == 3

    # GET single workflow
    r2 = client.get(f"/api/v1/workflows/{wf['id']}", headers=_auth(token))
    assert r2.status_code == 200
    assert r2.json()["data"]["id"] == wf["id"]


def test_submit_workflow(client: TestClient):
    token = _login(client, "pm", "PM123456")
    r = client.get("/api/v1/projects", headers=_auth(token))
    project_id = r.json()["data"]["items"][0]["id"]

    r = client.post(
        "/api/v1/workflows",
        json={"business_type": "project", "business_id": project_id, "project_id": project_id,
              "title": "提交测试", "workflow_type": "项目立项审批"},
        headers=_auth(token),
    )
    wf_id = r.json()["data"]["id"]

    r = client.post(f"/api/v1/workflows/{wf_id}/submit", json={}, headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "pending"


def test_approve_and_complete_workflow(client: TestClient):
    """Full approval cycle: submit → approve step1 (PM) → approve step2 (finance) → approve step3 (GM) → approved."""
    pm_token = _login(client, "pm", "PM123456")
    finance_token = _login(client, "finance", "Finance123456")
    gm_token = _login(client, "manager", "Manager123456")

    r = client.get("/api/v1/projects", headers=_auth(pm_token))
    project_id = r.json()["data"]["items"][0]["id"]

    # Create
    r = client.post(
        "/api/v1/workflows",
        json={"business_type": "project", "business_id": project_id, "project_id": project_id,
              "title": "完整审批流测试", "workflow_type": "项目立项审批"},
        headers=_auth(pm_token),
    )
    wf_id = r.json()["data"]["id"]

    # Submit (PM)
    client.post(f"/api/v1/workflows/{wf_id}/submit", json={}, headers=_auth(pm_token))

    # Step 1: PM approves
    r = client.post(f"/api/v1/workflows/{wf_id}/approve", json={"comment": "同意"}, headers=_auth(pm_token))
    assert r.status_code == 200
    assert r.json()["data"]["current_step"] == 2

    # Step 2: finance approves
    r = client.post(f"/api/v1/workflows/{wf_id}/approve", json={"comment": "财务确认"}, headers=_auth(finance_token))
    assert r.json()["data"]["current_step"] == 3

    # Step 3: GM approves → completed
    r = client.post(f"/api/v1/workflows/{wf_id}/approve", json={"comment": "批准"}, headers=_auth(gm_token))
    data = r.json()["data"]
    assert data["status"] == "approved"


def test_reject_workflow(client: TestClient):
    pm_token = _login(client, "pm", "PM123456")
    finance_token = _login(client, "finance", "Finance123456")

    r = client.get("/api/v1/projects", headers=_auth(pm_token))
    project_id = r.json()["data"]["items"][0]["id"]

    r = client.post(
        "/api/v1/workflows",
        json={"business_type": "project", "business_id": project_id, "project_id": project_id,
              "title": "驳回测试", "workflow_type": "项目立项审批"},
        headers=_auth(pm_token),
    )
    wf_id = r.json()["data"]["id"]
    client.post(f"/api/v1/workflows/{wf_id}/submit", json={}, headers=_auth(pm_token))

    # Finance rejects
    r = client.post(f"/api/v1/workflows/{wf_id}/reject", json={"comment": "材料不完整"}, headers=_auth(finance_token))
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "rejected"


def test_withdraw_workflow(client: TestClient):
    pm_token = _login(client, "pm", "PM123456")
    r = client.get("/api/v1/projects", headers=_auth(pm_token))
    project_id = r.json()["data"]["items"][0]["id"]

    r = client.post(
        "/api/v1/workflows",
        json={"business_type": "project", "business_id": project_id, "project_id": project_id,
              "title": "撤回测试", "workflow_type": "项目立项审批"},
        headers=_auth(pm_token),
    )
    wf_id = r.json()["data"]["id"]
    client.post(f"/api/v1/workflows/{wf_id}/submit", json={}, headers=_auth(pm_token))

    r = client.post(f"/api/v1/workflows/{wf_id}/withdraw", json={}, headers=_auth(pm_token))
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "withdrawn"


def test_project_submit_approval_shortcut(client: TestClient):
    """POST /projects/{id}/submit-approval creates + submits a workflow."""
    token = _login(client, "pm", "PM123456")
    r = client.get("/api/v1/projects", headers=_auth(token))
    project_id = r.json()["data"]["items"][0]["id"]

    r = client.post(f"/api/v1/projects/{project_id}/submit-approval", headers=_auth(token))
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["business_type"] == "project"
    assert data["business_id"] == project_id
    assert data["status"] == "pending"


def test_my_pending_and_initiated_workflows(client: TestClient):
    pm_token = _login(client, "pm", "PM123456")
    r = client.get("/api/v1/projects", headers=_auth(pm_token))
    project_id = r.json()["data"]["items"][0]["id"]

    # Create and submit
    r = client.post(
        "/api/v1/workflows",
        json={"business_type": "project", "business_id": project_id, "project_id": project_id,
              "title": "我的待办测试", "workflow_type": "项目立项审批"},
        headers=_auth(pm_token),
    )
    wf_id = r.json()["data"]["id"]
    client.post(f"/api/v1/workflows/{wf_id}/submit", json={}, headers=_auth(pm_token))

    # PM should see it in my-pending (PM is step 1 approver role)
    r = client.get("/api/v1/workflows/my-pending", headers=_auth(pm_token))
    assert r.status_code == 200
    ids = [w["id"] for w in r.json()["data"]]
    assert wf_id in ids

    # PM should see it in my-initiated
    r = client.get("/api/v1/workflows/my-initiated", headers=_auth(pm_token))
    assert r.status_code == 200
    assert any(w["id"] == wf_id for w in r.json()["data"])


def test_staff_cannot_create_workflow(client: TestClient):
    """Staff has workflow:view but not workflow:create."""
    token = _login(client, "staff", "Staff123456")
    r = client.get("/api/v1/projects", headers=_auth(token))
    project_id = r.json()["data"]["items"][0]["id"]

    r = client.post(
        "/api/v1/workflows",
        json={"business_type": "project", "business_id": project_id,
              "title": "无权限测试", "workflow_type": "项目立项审批"},
        headers=_auth(token),
    )
    assert r.status_code == 403
