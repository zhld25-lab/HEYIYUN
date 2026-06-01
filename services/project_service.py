from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset, load_all_data


def get_all_projects() -> pd.DataFrame:
    return get_dataset("projects")


def get_project_by_id(project_id: str) -> dict:
    projects = get_all_projects()
    rows = projects[projects["id"] == project_id]
    if rows.empty:
        return {}
    return rows.iloc[0].to_dict()


def get_project_summary() -> dict:
    projects = get_all_projects()
    workflows = get_dataset("workflows")
    documents = get_dataset("documents")
    return {
        "project_count": len(projects),
        "active_project_count": int(projects["status"].isin(["报装中", "施工中", "验收中"]).sum()),
        "contract_amount": float(projects["contract_amount"].sum()),
        "total_income": float(projects["received_amount"].sum()),
        "total_expense": float(projects["paid_amount"].sum()),
        "current_profit": float(projects["received_amount"].sum() - projects["actual_cost"].sum()),
        "high_risk_count": int(projects["risk_level"].isin(["高", "严重"]).sum()),
        "pending_approval_count": int((workflows["approval_status"] == "审批中").sum()),
        "missing_document_project_count": int(documents[documents["is_missing"]]["project_id"].nunique()),
        "average_profit_rate": float(projects["profit_rate"].mean()),
    }


def calculate_project_health_score(project: dict, related_data: dict | None = None) -> dict:
    score = 100
    reasons: list[str] = []
    actions: list[str] = []
    today = pd.Timestamp("2026-06-01")

    planned_end = pd.to_datetime(project.get("planned_end"))
    if project.get("status") not in {"已完工", "结算中"} and pd.notna(planned_end) and planned_end < today:
        delay_days = (today - planned_end).days
        penalty = min(30, 10 + delay_days // 20)
        score -= penalty
        reasons.append(f"计划工期已逾期 {delay_days} 天")
        actions.append("重排关键线路并明确送电验收节点")

    target_cost = float(project.get("target_cost", 0) or 0)
    actual_cost = float(project.get("actual_cost", 0) or 0)
    if target_cost > 0 and actual_cost > target_cost:
        ratio = actual_cost / target_cost
        penalty = 10 if ratio <= 1.1 else 20 if ratio <= 1.25 else 30
        score -= penalty
        reasons.append(f"成本比达到 {ratio:.1%}")
        actions.append("复核分包、材料与租赁费用，控制新增支出")

    output_progress = float(project.get("output_progress", 0) or 0)
    collection_progress = float(project.get("collection_progress", 0) or 0)
    if output_progress - collection_progress > 0.2:
        score -= 20
        reasons.append("收款进度落后产值进度超过 20%")
        actions.append("推进工程量确认、开票和回款")

    document_completion = float(project.get("document_completion", 1) or 1)
    if document_completion < 0.8:
        penalty = 20 if document_completion < 0.6 else 10
        score -= penalty
        reasons.append(f"资料完整率仅 {document_completion:.1%}")
        actions.append("按竣工归档清单补齐必传资料")

    if related_data:
        sq = related_data.get("safety_quality", pd.DataFrame())
        workflows = related_data.get("workflows", pd.DataFrame())
        unclosed_safety = 0
        unclosed_quality = 0
        if not sq.empty:
            unclosed_safety = int(((sq["category"] == "安全") & (~sq["is_closed"])).sum())
            unclosed_quality = int(((sq["category"] == "质量") & (~sq["is_closed"])).sum())
        if unclosed_safety:
            score -= min(30, 10 + unclosed_safety * 5)
            reasons.append(f"存在 {unclosed_safety} 项安全隐患未闭环")
            actions.append("安全员组织整改复查并关闭隐患")
        if unclosed_quality:
            score -= min(30, 10 + unclosed_quality * 5)
            reasons.append(f"存在 {unclosed_quality} 项质量问题未闭环")
            actions.append("质量员完成复验并归档记录")
        if not workflows.empty and workflows["is_overdue"].any():
            score -= 10
            reasons.append("存在审批超时")
            actions.append("催办当前节点，必要时升级审批")

    score = max(0, min(100, int(score)))
    if score >= 90:
        level, color = "优秀", "green"
    elif score >= 75:
        level, color = "正常", "blue"
    elif score >= 60:
        level, color = "关注", "orange"
    elif score >= 40:
        level, color = "风险", "red"
    else:
        level, color = "严重", "darkred"

    return {
        "health_score": score,
        "health_level": level,
        "risk_color": color,
        "risk_reasons": reasons or ["项目核心指标处于可控范围"],
        "recommended_actions": actions or ["保持月度复盘和关键节点跟踪"],
    }


def get_project_related_data(project_id: str) -> dict[str, pd.DataFrame]:
    data = load_all_data()
    related: dict[str, pd.DataFrame] = {}
    for key, df in data.items():
        if "project_id" in df.columns:
            related[key] = df[df["project_id"] == project_id].copy()
        else:
            related[key] = df.copy()
    return related


def filter_projects(
    projects: pd.DataFrame,
    keyword: str = "",
    project_type: str = "全部",
    voltage_level: str = "全部",
    status: str = "全部",
    manager: str = "全部",
    risk_level: str = "全部",
    profit_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    result = projects.copy()
    if keyword:
        result = result[
            result["project_name"].str.contains(keyword, case=False, na=False)
            | result["project_no"].str.contains(keyword, case=False, na=False)
        ]
    if project_type != "全部":
        result = result[result["project_type"] == project_type]
    if voltage_level != "全部":
        result = result[result["voltage_level"] == voltage_level]
    if status != "全部":
        result = result[result["status"] == status]
    if manager != "全部":
        result = result[result["project_manager"] == manager]
    if risk_level != "全部":
        result = result[result["risk_level"] == risk_level]
    if profit_range:
        low, high = profit_range
        result = result[(result["profit_rate"] >= low) & (result["profit_rate"] <= high)]
    return result

