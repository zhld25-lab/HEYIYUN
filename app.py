from __future__ import annotations

import streamlit as st

from components.charts import render_cashflow_chart, render_project_status_pie
from components.data_table import render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.metric_cards import render_kpi_grid
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.finance_service import get_monthly_cashflow
from services.permission_service import can_view_finance
from services.project_service import get_project_summary
from services.risk_service import get_high_risk_projects
from utils.formatters import format_money, to_display_df
from utils.session_state import init_session_state


def money_for_role(value: float, role: str) -> str:
    return format_money(value) if can_view_finance(role) else "***"


setup_page()
init_session_state()
role = render_sidebar()

render_page_header(
    "HEYIYUN 中国电力工程企业项目经营管理平台",
    "围绕项目全生命周期，贯通立项、报装、合同、采购、施工、成本、资金、安全质量、资料、审批和风险预警。",
)

summary = get_project_summary()
metrics = [
    {"label": "在建项目数", "value": str(summary["active_project_count"]), "delta": "报装中 / 施工中 / 验收中", "accent": "#0891b2"},
    {"label": "合同总额", "value": money_for_role(summary["contract_amount"], role), "delta": "承包合同口径", "accent": "#155e75"},
    {"label": "累计收入", "value": money_for_role(summary["total_income"], role), "delta": "已回款", "accent": "#16a34a"},
    {"label": "累计支出", "value": money_for_role(summary["total_expense"], role), "delta": "已付款", "accent": "#f97316"},
    {"label": "当前利润", "value": money_for_role(summary["current_profit"], role), "delta": "回款 - 实际成本", "accent": "#7c3aed"},
    {"label": "高风险项目数", "value": str(summary["high_risk_count"]), "delta": "高 / 严重", "accent": "#dc2626"},
    {"label": "审批待办数", "value": str(summary["pending_approval_count"]), "delta": "审批中流程", "accent": "#2563eb"},
    {"label": "资料缺失项目数", "value": str(summary["missing_document_project_count"]), "delta": "存在必传资料缺失", "accent": "#ca8a04"},
]
render_kpi_grid(metrics, columns=4)

st.divider()
st.subheader("经营概览")
projects = get_dataset("projects")
risks = get_dataset("risks")
workflows = get_dataset("workflows")

col1, col2 = st.columns([1.15, 0.85])
with col1:
    render_cashflow_chart(get_monthly_cashflow(), "月度收入、支出与净现金流")
with col2:
    render_project_status_pie(projects, "项目状态分布")

col3, col4 = st.columns(2)
with col3:
    high_risk = get_high_risk_projects(5)[["project_no", "project_name", "project_manager", "risk_level", "cost_ratio", "collection_progress", "document_completion"]]
    render_filterable_table(to_display_df(high_risk), "高风险项目 Top 5", height=280)
with col4:
    todo = workflows[workflows["approval_status"] == "审批中"].head(8)[["workflow_no", "workflow_type", "title", "project_name", "current_node", "current_handler", "is_overdue"]]
    render_filterable_table(to_display_df(todo), "我的待办审批", height=280)

recent = risks.sort_values("deadline").head(8)[["risk_no", "risk_type", "risk_level", "project_name", "trigger_reason", "responsible_person", "deadline", "current_status"]]
render_filterable_table(to_display_df(recent), "最近项目动态 / 风险提醒", height=300)

render_business_note(
    "首页用于模拟企业经营层和项目管理层的统一入口。所有指标均来自项目主数据，并与合同、成本、资金、审批、资料和风险记录联动。普通员工角色下金额会自动脱敏。"
)
