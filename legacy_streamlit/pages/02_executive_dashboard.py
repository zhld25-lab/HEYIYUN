from __future__ import annotations

import streamlit as st

from components.charts import (
    render_bar_ranking,
    render_cashflow_chart,
    render_cost_breakdown_chart,
    render_profit_ranking_chart,
    render_progress_scatter,
    render_project_status_pie,
    render_risk_distribution_chart,
)
from components.data_table import render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.metric_cards import render_kpi_grid
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.cost_service import calculate_cost_breakdown
from services.finance_service import get_monthly_cashflow
from services.material_service import get_supplier_ranking
from services.permission_service import can_view_finance
from services.project_service import get_project_related_data
from utils.formatters import format_money, format_percent, to_display_df
from utils.session_state import init_session_state


setup_page("决策驾驶舱")
init_session_state()
role = render_sidebar()
render_page_header("决策驾驶舱", "面向总经理、项目总监和财务负责人的公司级经营状态看板。")

projects = get_dataset("projects")
contracts = get_dataset("contracts")
costs = get_dataset("costs")
risks = get_dataset("risks")
workflows = get_dataset("workflows")

money = lambda v: format_money(v) if can_view_finance(role) else "***"
metrics = [
    {"label": "项目总数", "value": str(len(projects))},
    {"label": "在建项目数", "value": str(projects["status"].isin(["报装中", "施工中", "验收中"]).sum())},
    {"label": "本月新增项目", "value": str((projects["planned_start"].dt.month == 6).sum())},
    {"label": "合同总额", "value": money(projects["contract_amount"].sum())},
    {"label": "累计回款", "value": money(projects["received_amount"].sum())},
    {"label": "累计支出", "value": money(projects["paid_amount"].sum())},
    {"label": "应收款", "value": money(contracts["receivable"].sum())},
    {"label": "应付款", "value": money(contracts["payable"].sum())},
    {"label": "实际利润", "value": money((projects["contract_amount"] - projects["actual_cost"]).sum())},
    {"label": "平均利润率", "value": format_percent(projects["profit_rate"].mean()) if can_view_finance(role) else "***"},
    {"label": "高风险项目数", "value": str(projects["risk_level"].isin(["高", "严重"]).sum())},
    {"label": "审批超时数", "value": str(workflows["is_overdue"].sum())},
]
render_kpi_grid(metrics, columns=4)

col1, col2 = st.columns(2)
with col1:
    render_cashflow_chart(get_monthly_cashflow(), "月度收入、支出、净现金流")
with col2:
    render_project_status_pie(projects)

col3, col4 = st.columns(2)
with col3:
    render_profit_ranking_chart(projects)
with col4:
    render_progress_scatter(projects)

col5, col6 = st.columns(2)
with col5:
    render_cost_breakdown_chart(calculate_cost_breakdown(costs))
with col6:
    render_risk_distribution_chart(risks)

supplier = get_supplier_ranking().head(10).rename(columns={"supplier": "供应商", "total_amount": "采购金额"})
subcontract = contracts[contracts["contract_type"] == "分包合同"].groupby("party_b", as_index=False)["settlement_amount"].sum().sort_values("settlement_amount", ascending=False).head(10)
subcontract = subcontract.rename(columns={"party_b": "分包商", "settlement_amount": "结算金额"})
col7, col8 = st.columns(2)
with col7:
    render_bar_ranking(supplier, "采购金额", "供应商", "供应商采购金额排名")
with col8:
    render_bar_ranking(subcontract, "结算金额", "分包商", "分包商结算金额排名", color="#f97316")

st.subheader("预警中心")
warnings = risks[["risk_type", "risk_level", "project_name", "trigger_reason", "responsible_person", "deadline", "current_status", "recommended_action", "project_id"]]
render_filterable_table(to_display_df(warnings.drop(columns=["project_id"])), height=320)
if not warnings.empty:
    selected_project = st.selectbox("选择项目查看关联详情", warnings["project_id"].unique())
    related = get_project_related_data(selected_project)
    project = projects[projects["id"] == selected_project].iloc[0]
    st.info(f"项目：{project['project_name']}；合同金额：{money(project['contract_amount'])}；成本比：{format_percent(project['cost_ratio'])}；资料完整率：{format_percent(project['document_completion'])}")
    cols = st.columns(3)
    cols[0].dataframe(to_display_df(related["contracts"].head(5)), use_container_width=True, hide_index=True)
    cols[1].dataframe(to_display_df(related["costs"].head(5)), use_container_width=True, hide_index=True)
    cols[2].dataframe(to_display_df(related["finance"].head(5)), use_container_width=True, hide_index=True)

render_business_note("驾驶舱从公司经营视角汇总项目状态、利润、现金流、供应商、分包商和风险预警，适合管理层进行月度经营分析。")

