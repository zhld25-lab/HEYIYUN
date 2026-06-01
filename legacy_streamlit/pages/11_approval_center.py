from __future__ import annotations

import streamlit as st

from components.data_table import render_export_button, render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from components.workflow_view import render_workflow_actions, render_workflow_status
from data.data_loader import get_dataset
from services.permission_service import can_approve
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("审批中心")
init_session_state()
role = render_sidebar()
render_page_header("审批中心", "模拟 OA / BPM 审批流，覆盖立项、合同、采购、付款、报销、签证、结算、材料领用、设备租赁、安全质量整改和竣工资料。")

workflows = get_dataset("workflows")
c1, c2, c3 = st.columns(3)
wtype = c1.selectbox("流程类型", ["全部"] + sorted(workflows["workflow_type"].unique()))
status = c2.selectbox("审批状态", ["全部"] + sorted(workflows["approval_status"].unique()))
overdue = c3.selectbox("是否超时", ["全部", "是", "否"])
filtered = workflows.copy()
if wtype != "全部":
    filtered = filtered[filtered["workflow_type"] == wtype]
if status != "全部":
    filtered = filtered[filtered["approval_status"] == status]
if overdue != "全部":
    filtered = filtered[filtered["is_overdue"] == (overdue == "是")]

render_export_button(to_display_df(filtered), "workflow_list_export.xlsx")
render_filterable_table(to_display_df(filtered), "审批列表", height=360)

if not filtered.empty:
    selected = st.selectbox("选择流程查看轨迹", filtered["id"], format_func=lambda x: filtered.loc[filtered["id"] == x, "title"].iloc[0])
    workflow = filtered[filtered["id"] == selected].iloc[0].to_dict()
    render_workflow_status(workflow)
    if can_approve(role, workflow["workflow_type"]):
        render_workflow_actions(selected)
    else:
        st.warning("当前角色无审批操作权限，仅可查看流程状态。")

render_business_note("审批中心当前为模拟流程：发起人 → 部门负责人 → 项目经理 → 财务负责人 → 总经理 → 完成 / 驳回。")

