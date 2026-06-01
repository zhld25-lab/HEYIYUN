from __future__ import annotations

import streamlit as st

from components.data_table import render_export_button, render_filterable_table
from components.detail_tabs import render_project_detail_tabs
from components.filters import keyword_filter, select_filter
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.permission_service import mask_sensitive_fields
from services.project_service import filter_projects, get_project_related_data
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("项目中心")
init_session_state()
role = render_sidebar()
render_page_header("项目中心", "项目是系统主线，所有合同、成本、资金、材料、设备、资料、审批和风险均围绕项目关联。")

projects = get_dataset("projects")
with st.expander("筛选条件", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    keyword = c1.text_input("项目名称 / 编号")
    project_type = c2.selectbox("项目类型", ["全部"] + sorted(projects["project_type"].unique()))
    voltage = c3.selectbox("电压等级", ["全部"] + sorted(projects["voltage_level"].unique()))
    status = c4.selectbox("项目状态", ["全部"] + sorted(projects["status"].unique()))
    c5, c6, c7 = st.columns(3)
    manager = c5.selectbox("项目经理", ["全部"] + sorted(projects["project_manager"].unique()))
    risk = c6.selectbox("风险等级", ["全部", "低", "中", "高", "严重"])
    profit = c7.slider("利润率区间", min_value=-0.5, max_value=0.5, value=(-0.2, 0.4), step=0.01)

filtered = filter_projects(projects, keyword, project_type, voltage, status, manager, risk, profit)
display_cols = [
    "project_no", "project_name", "project_type", "voltage_level", "owner", "project_manager", "status",
    "planned_start", "planned_end", "contract_amount", "target_cost", "actual_cost", "received_amount",
    "paid_amount", "output_progress", "collection_progress", "cost_ratio", "profit_rate", "risk_level", "document_completion",
]
masked = mask_sensitive_fields(filtered[display_cols], role)
render_export_button(to_display_df(masked), "project_list_export.xlsx")
render_filterable_table(to_display_df(masked), "项目列表", height=380)

if not filtered.empty:
    selected = st.selectbox("选择项目查看详情", filtered["id"], format_func=lambda x: filtered.loc[filtered["id"] == x, "project_name"].iloc[0])
    project = projects[projects["id"] == selected].iloc[0].to_dict()
    related = get_project_related_data(selected)
    st.subheader("项目详情")
    render_project_detail_tabs(project, related)

render_business_note("项目中心用于贯通项目全生命周期数据，重点展示项目健康度、成本偏差、进度节点、资金计划、资料完整率和风险闭环。")

