from __future__ import annotations

import pandas as pd

from config.role_config import APPROVAL_ROLES, FINANCE_ROLES, FULL_ACCESS_ROLES, ROLE_MODULES

SENSITIVE_COLUMNS = [
    "contract_amount",
    "target_cost",
    "actual_cost",
    "received_amount",
    "paid_amount",
    "profit",
    "expected_profit",
    "profit_rate",
    "amount",
    "settlement_amount",
    "invoice_amount",
    "receivable",
    "payable",
    "budget_unit_price",
    "purchase_unit_price",
    "total_amount",
    "rental_price",
    "rental_amount",
]


def get_visible_modules_by_role(role: str) -> list[str]:
    modules = ROLE_MODULES.get(role, ["首页工作台"])
    if modules == ["全部模块"]:
        return ["全部模块"]
    return modules


def can_view_finance(role: str) -> bool:
    return role in FINANCE_ROLES


def can_approve(role: str, workflow_type: str | None = None) -> bool:
    if role in FULL_ACCESS_ROLES:
        return True
    if workflow_type and "付款" in workflow_type:
        return role in {"财务负责人", "总经理"}
    return role in APPROVAL_ROLES


def mask_sensitive_fields(df: pd.DataFrame, role: str) -> pd.DataFrame:
    if df is None or df.empty or can_view_finance(role):
        return df
    result = df.copy()
    for col in SENSITIVE_COLUMNS:
        if col in result.columns:
            result[col] = "***"
    return result

