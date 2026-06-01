from __future__ import annotations

import streamlit as st

from components.charts import render_cashflow_chart, render_cost_breakdown_chart, render_profit_ranking_chart
from components.data_table import render_export_button, render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.cost_service import calculate_cost_breakdown
from services.finance_service import get_monthly_cashflow
from services.permission_service import mask_sensitive_fields
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("成本资金中心")
init_session_state()
role = render_sidebar()
render_page_header("成本资金中心", "统一展示项目成本、费用报销、付款、回款、发票、资金计划和保证金。")

costs = get_dataset("costs")
finance = get_dataset("finance")
projects = get_dataset("projects")
contracts = get_dataset("contracts")

project = st.selectbox("所属项目", ["全部"] + sorted(projects["project_name"].unique()))
cost_filtered = costs.copy()
finance_filtered = finance.copy()
if project != "全部":
    cost_filtered = cost_filtered[cost_filtered["project_name"] == project]
    finance_filtered = finance_filtered[finance_filtered["project_name"] == project]

tabs = st.tabs(["成本台账", "成本归集", "成本分析", "费用报销", "付款管理", "回款管理", "发票管理", "资金计划", "保证金管理"])
with tabs[0]:
    render_export_button(to_display_df(mask_sensitive_fields(cost_filtered, role)), "cost_ledger_export.xlsx")
    render_filterable_table(to_display_df(mask_sensitive_fields(cost_filtered, role)), height=360)
with tabs[1]:
    render_filterable_table(to_display_df(mask_sensitive_fields(cost_filtered.groupby(["project_name", "cost_type"], as_index=False)["amount"].sum(), role)), "按项目和成本类型归集")
with tabs[2]:
    col1, col2 = st.columns(2)
    with col1:
        render_cost_breakdown_chart(calculate_cost_breakdown(cost_filtered))
    with col2:
        render_profit_ranking_chart(projects)
    render_cashflow_chart(get_monthly_cashflow())
with tabs[3]:
    render_filterable_table(to_display_df(mask_sensitive_fields(cost_filtered[cost_filtered["cost_type"] == "费用报销"], role)), height=320)
with tabs[4]:
    payments = finance_filtered[finance_filtered["direction"] == "支出"]
    render_filterable_table(to_display_df(mask_sensitive_fields(payments, role)), height=320)
with tabs[5]:
    receipts = finance_filtered[finance_filtered["direction"] == "收入"]
    render_filterable_table(to_display_df(mask_sensitive_fields(receipts, role)), height=320)
with tabs[6]:
    invoices = finance_filtered[finance_filtered["finance_type"] == "发票"]
    render_filterable_table(to_display_df(mask_sensitive_fields(invoices, role)), height=320)
with tabs[7]:
    plans = finance_filtered[finance_filtered["finance_type"] == "资金计划"]
    render_filterable_table(to_display_df(mask_sensitive_fields(plans, role)), height=320)
with tabs[8]:
    deposits = finance_filtered[finance_filtered["finance_type"] == "保证金"]
    render_filterable_table(to_display_df(mask_sensitive_fields(deposits, role)), height=320)

render_business_note("成本资金中心把成本台账、付款、回款、发票和现金流放在同一视图下，用于判断项目利润和资金风险。")

