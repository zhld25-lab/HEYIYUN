from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    project_count: int
    active_project_count: int
    contract_amount: Any = 0
    received_amount: Any = 0
    paid_amount: Any = 0
    current_profit: Any = 0
    high_risk_count: int = 0


class ProjectStatusItem(BaseModel):
    status: str
    count: int
