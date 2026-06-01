from __future__ import annotations


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_seeded_finance_lists(client, admin_token):
    for ep, expected in [("contracts", 30), ("costs", 80), ("payments", 50), ("receipts", 50), ("invoices", 50)]:
        resp = client.get(f"/api/v1/{ep}", headers=_auth(admin_token))
        assert resp.status_code == 200, resp.text
        assert resp.json()["data"]["total"] == expected


def test_project_finance_summary(client, admin_token):
    resp = client.get("/api/v1/projects/1/finance-summary", headers=_auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "contract_amount" in data and "profit" in data


def test_receipt_create_recalculates_project(client, admin_token):
    before = float(
        client.get("/api/v1/projects/1/finance-summary", headers=_auth(admin_token)).json()["data"]["received_amount"]
    )
    resp = client.post(
        "/api/v1/receipts",
        json={"receipt_code": "HK-UT-1", "project_id": 1, "receipt_amount": 1234000, "payer_name": "甲方"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 200, resp.text
    rid = resp.json()["data"]["id"]
    after = float(
        client.get("/api/v1/projects/1/finance-summary", headers=_auth(admin_token)).json()["data"]["received_amount"]
    )
    assert round(after - before, 2) == 1234000.0

    # audit log recorded
    logs = client.get(
        "/api/v1/system/audit-logs",
        params={"resource_type": "receipt", "resource_id": str(rid)},
        headers=_auth(admin_token),
    )
    assert any(i["action"] == "CREATE" for i in logs.json()["data"]["items"])

    # soft delete restores the aggregate
    assert client.delete(f"/api/v1/receipts/{rid}", headers=_auth(admin_token)).status_code == 200
    final = float(
        client.get("/api/v1/projects/1/finance-summary", headers=_auth(admin_token)).json()["data"]["received_amount"]
    )
    assert round(final, 2) == round(before, 2)


def test_contract_masking_for_staff(client, staff_token):
    resp = client.get("/api/v1/contracts?page_size=1", headers=_auth(staff_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["items"][0]["contract_amount"] == "***"


def test_staff_cannot_create_contract(client, staff_token):
    resp = client.post(
        "/api/v1/contracts",
        json={"contract_code": "HT-NO", "contract_name": "x", "contract_type": "承包合同", "project_id": 1},
        headers=_auth(staff_token),
    )
    assert resp.status_code == 403


def test_pm_can_create_contract_but_not_delete_cost(client):
    pm = client.post("/api/v1/auth/login", json={"username": "pm", "password": "PM123456"}).json()["data"][
        "access_token"
    ]
    create = client.post(
        "/api/v1/contracts",
        json={"contract_code": "HT-PM-UT", "contract_name": "pm合同", "contract_type": "采购合同", "project_id": 1},
        headers=_auth(pm),
    )
    assert create.status_code == 200, create.text

    admin = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin123456"}).json()["data"][
        "access_token"
    ]
    cost_id = client.get("/api/v1/costs?page_size=1", headers=_auth(admin)).json()["data"]["items"][0]["id"]
    assert client.delete(f"/api/v1/costs/{cost_id}", headers=_auth(pm)).status_code == 403


def test_dashboard_finance_endpoints(client, admin_token):
    for ep in ["finance-summary", "cashflow", "cost-breakdown", "project-profit-top"]:
        assert client.get(f"/api/v1/dashboard/{ep}", headers=_auth(admin_token)).status_code == 200
