from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def get_all_workflows() -> pd.DataFrame:
    return get_dataset("workflows")


def get_pending_tasks() -> pd.DataFrame:
    workflows = get_all_workflows()
    return workflows[workflows["approval_status"] == "审批中"].copy()


def get_workflow_by_id(workflow_id: str) -> dict:
    workflows = get_all_workflows()
    rows = workflows[workflows["id"] == workflow_id]
    return rows.iloc[0].to_dict() if not rows.empty else {}


def simulate_approve(workflow_id: str, opinion: str = "同意") -> dict:
    workflow = get_workflow_by_id(workflow_id)
    return {"workflow_id": workflow_id, "success": bool(workflow), "message": f"已模拟通过：{workflow.get('title', workflow_id)}，意见：{opinion}"}


def simulate_reject(workflow_id: str, opinion: str = "请补充资料") -> dict:
    workflow = get_workflow_by_id(workflow_id)
    return {"workflow_id": workflow_id, "success": bool(workflow), "message": f"已模拟驳回：{workflow.get('title', workflow_id)}，意见：{opinion}"}


def detect_overdue_workflows() -> pd.DataFrame:
    workflows = get_all_workflows()
    return workflows[workflows["is_overdue"]].copy()

