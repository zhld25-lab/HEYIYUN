from __future__ import annotations


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_list_projects(client, admin_token):
    resp = client.get("/api/v1/projects", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 3


def test_create_project_and_audit(client, admin_token):
    payload = {
        "project_code": "PJ-TEST-001",
        "project_name": "测试新建项目",
        "project_type": "10kV配电工程",
        "voltage_level": "10kV",
        "contract_amount": 1000000,
        "target_cost": 800000,
        "actual_cost": 200000,
    }
    resp = client.post("/api/v1/projects", json=payload, headers=_auth(admin_token))
    assert resp.status_code == 200, resp.text
    project_id = resp.json()["data"]["id"]

    # Audit log recorded
    logs = client.get(
        "/api/v1/system/audit-logs",
        params={"resource_type": "project", "resource_id": str(project_id)},
        headers=_auth(admin_token),
    )
    assert logs.status_code == 200
    assert any(item["action"] == "CREATE" for item in logs.json()["data"]["items"])


def test_create_duplicate_code(client, admin_token):
    payload = {
        "project_code": "PJ-2025-001",
        "project_name": "重复编号",
        "project_type": "10kV配电工程",
    }
    resp = client.post("/api/v1/projects", json=payload, headers=_auth(admin_token))
    assert resp.status_code == 409


def test_invalid_date_range(client, admin_token):
    payload = {
        "project_code": "PJ-TEST-DATE",
        "project_name": "日期校验",
        "project_type": "10kV配电工程",
        "planned_start_date": "2025-06-01",
        "planned_end_date": "2025-01-01",
    }
    resp = client.post("/api/v1/projects", json=payload, headers=_auth(admin_token))
    assert resp.status_code == 422


def test_financial_masking_for_staff(client, staff_token):
    resp = client.get("/api/v1/projects", headers=_auth(staff_token))
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert items, "expected seeded projects"
    assert items[0]["contract_amount"] == "***"


def test_staff_cannot_create(client, staff_token):
    payload = {
        "project_code": "PJ-STAFF-001",
        "project_name": "无权限新建",
        "project_type": "10kV配电工程",
    }
    resp = client.post("/api/v1/projects", json=payload, headers=_auth(staff_token))
    assert resp.status_code == 403
