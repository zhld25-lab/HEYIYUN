from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ProjectFinanceSummary(BaseModel):
    project_id: int
    contract_amount: Any = 0
    target_cost: Any = 0
    actual_cost: Any = 0
    received_amount: Any = 0
    paid_amount: Any = 0
    receivable_amount: Any = 0
    payable_amount: Any = 0
    profit: Any = 0
    profit_margin: Any = 0
    collection_progress: float = 0
    cost_ratio: float = 0


class DashboardFinanceSummary(BaseModel):
    total_contract_amount: Any = 0
    total_actual_cost: Any = 0
    total_received: Any = 0
    total_paid: Any = 0
    total_receivable: Any = 0
    total_payable: Any = 0
    total_profit: Any = 0


class CashflowItem(BaseModel):
    month: str
    received: Any = 0
    paid: Any = 0
    net: Any = 0


class CostBreakdownItem(BaseModel):
    cost_type: str
    amount: Any = 0


class ProjectProfitItem(BaseModel):
    project_id: int
    project_name: str
    profit: Any = 0
