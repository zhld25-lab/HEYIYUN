from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def get_all_contracts() -> pd.DataFrame:
    return get_dataset("contracts")


def get_contracts_by_project(project_id: str) -> pd.DataFrame:
    contracts = get_all_contracts()
    return contracts[contracts["project_id"] == project_id].copy()


def get_contract_summary() -> dict:
    contracts = get_all_contracts()
    return {
        "contract_count": len(contracts),
        "contract_amount": float(contracts["contract_amount"].sum()),
        "settlement_amount": float(contracts["settlement_amount"].sum()),
        "invoice_amount": float(contracts["invoice_amount"].sum()),
        "receivable": float(contracts["receivable"].sum()),
        "payable": float(contracts["payable"].sum()),
        "unarchived_count": int((contracts["archive_status"] != "已归档").sum()),
    }


def calculate_contract_risk(contract: dict) -> list[str]:
    risks: list[str] = []
    if contract.get("approval_status") != "已通过":
        risks.append("合同未完成审批")
    if contract.get("archive_status") != "已归档":
        risks.append("合同未归档")
    if float(contract.get("paid_amount", 0) or 0) > float(contract.get("settlement_amount", 0) or 0):
        risks.append("付款金额超过结算金额")
    if float(contract.get("invoice_amount", 0) or 0) > float(contract.get("settlement_amount", 0) or 0) * 1.05:
        risks.append("发票金额异常")
    if float(contract.get("receivable", 0) or 0) > float(contract.get("contract_amount", 0) or 0) * 0.35:
        risks.append("回款滞后")
    return risks or ["暂无明显合同风险"]

