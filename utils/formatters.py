from __future__ import annotations

import pandas as pd

from utils.constants import GLOBAL_COLUMN_MAP, MONEY_COLUMNS


def format_money(value, unit: str = "万元") -> str:
    if value is None or pd.isna(value):
        return "-"
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return str(value)
    if unit == "万元":
        return f"{amount / 10000:,.1f} 万元"
    return f"¥{amount:,.2f}"


def format_percent(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    value = float(value)
    if value <= 1:
        value *= 100
    return f"{value:.1f}%"


def format_date(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return pd.to_datetime(value).strftime("%Y-%m-%d")


def to_display_df(df: pd.DataFrame, columns_map: dict[str, str] | None = None) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    result = df.copy()
    for col in result.columns:
        if "amount" in col or col in MONEY_COLUMNS or col in {"profit", "target_cost", "actual_cost", "paid", "unpaid", "receivable", "payable"}:
            result[col] = result[col].apply(format_money)
        if "progress" in col or "rate" in col or "completion" in col or col == "cost_ratio":
            result[col] = result[col].apply(format_percent)
        if "date" in col or col.endswith("_start") or col.endswith("_end") or col.endswith("_time"):
            result[col] = result[col].apply(format_date)
    result = result.rename(columns=columns_map or GLOBAL_COLUMN_MAP)
    return result


def status_badge_text(status: str) -> str:
    return f"● {status}"
