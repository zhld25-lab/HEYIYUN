from __future__ import annotations

import streamlit as st

from components.data_table import render_export_button, render_filterable_table
from components.detail_tabs import render_contract_detail_tabs
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.contract_service import calculate_contract_risk, get_contract_summary
from services.permission_service import mask_sensitive_fields
from utils.formatters import format_money, to_display_df
from utils.session_state import init_session_state


setup_page("合同中心")
init_session_state()
role = render_sidebar()
render_page_header("合同中心", "管理承包合同、分包合同、采购合同、设备租赁合同和周材租赁合同。")

contracts = get_dataset("contracts")
summary = get_contract_summary()
cols = st.columns(5)
cols[0].metric("合同数量", summary["contract_count"])
cols[1].metric("合同总额", format_money(summary["contract_amount"]) if role in {"总经理", "财务负责人", "系统管理员"} else "***")
cols[2].metric("结算金额", format_money(summary["settlement_amount"]) if role in {"总经理", "财务负责人", "系统管理员"} else "***")
cols[3].metric("应收款", format_money(summary["receivable"]) if role in {"总经理", "财务负责人", "系统管理员"} else "***")
cols[4].metric("未归档合同", summary["unarchived_count"])

c1, c2, c3 = st.columns(3)
ctype = c1.selectbox("合同类型", ["全部"] + sorted(contracts["contract_type"].unique()))
status = c2.selectbox("合同状态", ["全部"] + sorted(contracts["contract_status"].unique()))
archive = c3.selectbox("归档状态", ["全部"] + sorted(contracts["archive_status"].unique()))
filtered = contracts.copy()
if ctype != "全部":
    filtered = filtered[filtered["contract_type"] == ctype]
if status != "全部":
    filtered = filtered[filtered["contract_status"] == status]
if archive != "全部":
    filtered = filtered[filtered["archive_status"] == archive]

cols_show = ["contract_no", "contract_name", "contract_type", "project_name", "party_a", "party_b", "contract_amount", "settlement_amount", "invoice_amount", "received_amount", "paid_amount", "receivable", "payable", "contract_status", "approval_status", "archive_status"]
masked = mask_sensitive_fields(filtered[cols_show], role)
render_export_button(to_display_df(masked), "contract_list_export.xlsx")
render_filterable_table(to_display_df(masked), "合同列表", height=360)

if not filtered.empty:
    selected = st.selectbox("选择合同查看详情", filtered["id"], format_func=lambda x: filtered.loc[filtered["id"] == x, "contract_name"].iloc[0])
    contract = filtered[filtered["id"] == selected].iloc[0].to_dict()
    render_contract_detail_tabs(contract)
    st.subheader("合同风险")
    for item in calculate_contract_risk(contract):
        st.warning(item) if "风险" in item or "未" in item or "异常" in item or "滞后" in item else st.success(item)

render_business_note("合同中心强调合同与项目、成本分类、资金流水、发票、结算和审批流程的强关联。")

