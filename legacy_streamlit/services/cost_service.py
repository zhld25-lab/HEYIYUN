from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def get_all_costs() -> pd.DataFrame:
    return get_dataset("costs")


def get_costs_by_project(project_id: str) -> pd.DataFrame:
    costs = get_all_costs()
    return costs[costs["project_id"] == project_id].copy()


def calculate_cost_breakdown(costs: pd.DataFrame) -> pd.DataFrame:
    if costs.empty:
        return pd.DataFrame(columns=["cost_type", "amount"])
    return costs.groupby("cost_type", as_index=False)["amount"].sum().sort_values("amount", ascending=False)


def calculate_cost_variance(project: dict) -> dict:
    target = float(project.get("target_cost", 0) or 0)
    actual = float(project.get("actual_cost", 0) or 0)
    variance = actual - target
    return {
        "target_cost": target,
        "actual_cost": actual,
        "variance": variance,
        "variance_rate": variance / target if target else 0,
    }


def detect_cost_overrun(project: dict) -> dict:
    target = float(project.get("target_cost", 0) or 0)
    actual = float(project.get("actual_cost", 0) or 0)
    if target <= 0:
        return {"level": "未知", "message": "缺少目标成本"}
    if actual <= target:
        return {"level": "正常", "message": "实际成本未超过目标成本"}
    if actual <= target * 1.1:
        return {"level": "中", "message": "实际成本超过目标成本但未超过 10%"}
    if actual <= target * 1.25:
        return {"level": "高", "message": "实际成本超过目标成本 10%-25%"}
    return {"level": "严重", "message": "实际成本超过目标成本 25% 以上"}

