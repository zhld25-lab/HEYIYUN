from __future__ import annotations

import streamlit as st

from components.data_table import render_export_button, render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.risk_badge import render_risk_summary
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.project_service import get_project_related_data
from services.risk_service import calculate_project_risk
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("风险预警中心")
init_session_state()
role = render_sidebar()
render_page_header("风险预警中心", "统一展示工期、成本、资金、合同、采购、材料、设备、安全、质量、资料和审批风险。")

risks = get_dataset("risks")
projects = get_dataset("projects")
c1, c2, c3 = st.columns(3)
rtype = c1.selectbox("风险类型", ["全部"] + sorted(risks["risk_type"].unique()))
level = c2.selectbox("风险等级", ["全部", "低", "中", "高", "严重"])
closed = c3.selectbox("是否闭环", ["全部", "是", "否"])
filtered = risks.copy()
if rtype != "全部":
    filtered = filtered[filtered["risk_type"] == rtype]
if level != "全部":
    filtered = filtered[filtered["risk_level"] == level]
if closed != "全部":
    filtered = filtered[filtered["is_closed"] == (closed == "是")]

render_export_button(to_display_df(filtered), "risk_warning_export.xlsx")
render_filterable_table(to_display_df(filtered), "风险预警列表", height=380)

st.subheader("项目风险评分模拟")
selected_project = st.selectbox("选择项目计算风险", projects["id"], format_func=lambda x: projects.loc[projects["id"] == x, "project_name"].iloc[0])
project = projects[projects["id"] == selected_project].iloc[0].to_dict()
related = get_project_related_data(selected_project)
render_risk_summary(calculate_project_risk(project, related))

render_business_note("风险评分由工期、成本、收款、付款、安全、质量、资料和审批规则共同触发，输出风险等级、原因和建议动作。")

