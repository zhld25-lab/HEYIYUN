from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def _level_from_score(score: int) -> str:
    if score >= 85:
        return "严重"
    if score >= 65:
        return "高"
    if score >= 35:
        return "中"
    return "低"


def calculate_project_risk(project: dict, related_data: dict | None = None) -> dict:
    score = 0
    reasons: list[str] = []
    actions: list[str] = []
    today = pd.Timestamp("2026-06-01")

    planned_end = pd.to_datetime(project.get("planned_end"))
    if project.get("status") not in {"已完工", "结算中"} and pd.notna(planned_end) and planned_end < today:
        days = (today - planned_end).days
        score += min(30, 12 + days // 15)
        reasons.append(f"工期延期 {days} 天")
        actions.append("压实关键节点责任，优先推进送电验收条件")

    target_cost = float(project.get("target_cost", 0) or 0)
    actual_cost = float(project.get("actual_cost", 0) or 0)
    if target_cost > 0 and actual_cost > target_cost:
        ratio = actual_cost / target_cost
        score += 12 if ratio <= 1.1 else 24 if ratio <= 1.25 else 35
        reasons.append(f"成本超预算，成本比 {ratio:.1%}")
        actions.append("复核采购超价、分包签证和费用报销")

    output_progress = float(project.get("output_progress", 0) or 0)
    collection_progress = float(project.get("collection_progress", 0) or 0)
    if output_progress - collection_progress > 0.2:
        score += 25
        reasons.append("收款进度低于产值进度 20% 以上")
        actions.append("推进工程量确认、开票和回款计划")

    doc_completion = float(project.get("document_completion", 1) or 1)
    if doc_completion < 0.8:
        score += 22 if doc_completion < 0.6 else 12
        reasons.append(f"资料完整率 {doc_completion:.1%}")
        actions.append("资料员补齐必传资料并发起审核")

    if related_data:
        workflows = related_data.get("workflows", pd.DataFrame())
        safety_quality = related_data.get("safety_quality", pd.DataFrame())
        contracts = related_data.get("contracts", pd.DataFrame())
        if not workflows.empty and workflows["is_overdue"].any():
            score += 12
            reasons.append("存在审批超时")
            actions.append("催办或升级当前审批节点")
        if not safety_quality.empty:
            unclosed_safety = int(((safety_quality["category"] == "安全") & (~safety_quality["is_closed"])).sum())
            unclosed_quality = int(((safety_quality["category"] == "质量") & (~safety_quality["is_closed"])).sum())
            if unclosed_safety:
                score += min(25, 10 + unclosed_safety * 5)
                reasons.append(f"{unclosed_safety} 项安全隐患未闭环")
                actions.append("完成整改、复查和闭环")
            if unclosed_quality:
                score += min(25, 10 + unclosed_quality * 5)
                reasons.append(f"{unclosed_quality} 项质量问题未闭环")
                actions.append("组织复验并补充验收资料")
        if not contracts.empty:
            abnormal_payment = (contracts["paid_amount"] > contracts["settlement_amount"] * 1.02).any()
            if abnormal_payment:
                score += 15
                reasons.append("存在付款超过结算金额的合同")
                actions.append("财务复核付款计划和结算依据")

    score = max(0, min(100, int(score)))
    return {
        "risk_score": score,
        "risk_level": _level_from_score(score),
        "risk_reasons": reasons or ["未触发重大风险规则"],
        "recommended_actions": actions or ["保持月度经营复盘和风险监测"],
    }


def detect_risk_items() -> pd.DataFrame:
    return get_dataset("risks")


def get_high_risk_projects(limit: int = 5) -> pd.DataFrame:
    projects = get_dataset("projects")
    risk_order = {"严重": 4, "高": 3, "中": 2, "低": 1}
    result = projects.copy()
    result["risk_order"] = result["risk_level"].map(risk_order)
    return result.sort_values(["risk_order", "cost_ratio"], ascending=False).head(limit).drop(columns=["risk_order"])


def get_risk_recommendations(risk_type: str) -> str:
    recommendations = {
        "工期风险": "重排进度计划，优先保障停送电窗口、关键设备到货和验收资源。",
        "成本风险": "复核目标成本、采购价格、分包结算和现场签证。",
        "资金风险": "推动工程量确认、发票开具和回款节点兑现。",
        "安全风险": "立即整改隐患，复查通过前不得进入下一道高风险工序。",
        "质量风险": "完成缺陷整改、复验和验收资料归档。",
        "资料风险": "按项目资料清单补齐必传项并完成审核。",
        "审批风险": "催办当前节点，超过时限后升级至上级负责人。",
    }
    return recommendations.get(risk_type, "责任部门复核预警数据并形成闭环处理记录。")

