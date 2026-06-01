from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def get_cashflow_summary() -> dict:
    projects = get_dataset("projects")
    contracts = get_dataset("contracts")
    return {
        "income": float(projects["received_amount"].sum()),
        "expense": float(projects["paid_amount"].sum()),
        "net_cashflow": float(projects["received_amount"].sum() - projects["paid_amount"].sum()),
        "receivable": float(contracts["receivable"].sum()),
        "payable": float(contracts["payable"].sum()),
    }


def calculate_receivable(project_id: str | None = None) -> float:
    contracts = get_dataset("contracts")
    if project_id:
        contracts = contracts[contracts["project_id"] == project_id]
    return float(contracts["receivable"].sum())


def calculate_payable(project_id: str | None = None) -> float:
    contracts = get_dataset("contracts")
    if project_id:
        contracts = contracts[contracts["project_id"] == project_id]
    return float(contracts["payable"].sum())


def calculate_profit(project_id: str | None = None) -> float:
    projects = get_dataset("projects")
    if project_id:
        projects = projects[projects["id"] == project_id]
    return float((projects["contract_amount"] - projects["actual_cost"]).sum())


def get_monthly_cashflow() -> pd.DataFrame:
    finance = get_dataset("finance")
    df = finance.copy()
    df["month"] = pd.to_datetime(df["business_date"]).dt.to_period("M").astype(str)
    grouped = df.pivot_table(index="month", columns="direction", values="amount", aggfunc="sum", fill_value=0).reset_index()
    for col in ["收入", "支出", "计划"]:
        if col not in grouped.columns:
            grouped[col] = 0.0
    grouped["净现金流"] = grouped["收入"] - grouped["支出"]
    return grouped.sort_values("month")

def get_project_finance(project_id: str) -> pd.DataFrame:
    finance = get_dataset("finance")
    return finance[finance["project_id"] == project_id].copy()

