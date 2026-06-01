from __future__ import annotations

import streamlit as st

from components.data_table import render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from components.workflow_view import render_workflow_actions, render_workflow_status
from data.data_loader import get_dataset
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("首页工作台")
init_session_state()
role = render_sidebar()
render_page_header("首页工作台", "模拟企业员工登录后的个人待办、风险提醒和快捷业务入口。")

workflows = get_dataset("workflows")
risks = get_dataset("risks")

col1, col2 = st.columns(2)
with col1:
    type_filter = st.selectbox("待办类型", ["全部"] + sorted(workflows["workflow_type"].unique().tolist()))
with col2:
    overdue_filter = st.selectbox("是否超时", ["全部", "是", "否"])

todo = workflows[workflows["approval_status"] == "审批中"].copy()
if type_filter != "全部":
    todo = todo[todo["workflow_type"] == type_filter]
if overdue_filter != "全部":
    todo = todo[todo["is_overdue"] == (overdue_filter == "是")]

todo_view = todo[["workflow_no", "workflow_type", "title", "project_name", "initiator", "current_node", "arrival_time", "is_overdue", "id"]]
render_filterable_table(to_display_df(todo_view.drop(columns=["id"])), "我的待办", height=320)

if not todo.empty:
    selected = st.selectbox("选择待办查看详情", todo["id"], format_func=lambda x: todo.loc[todo["id"] == x, "title"].iloc[0])
    workflow = todo[todo["id"] == selected].iloc[0].to_dict()
    st.subheader("待办详情与审批流轨迹")
    render_workflow_status(workflow)
    render_workflow_actions(selected)

tab_done, tab_started, tab_risk, tab_quick = st.tabs(["我的已办", "我的发起", "项目风险提醒", "快捷入口"])
with tab_done:
    done = workflows[workflows["approval_status"] != "审批中"][["workflow_type", "title", "project_name", "approval_result", "arrival_time", "approval_opinion"]]
    render_filterable_table(to_display_df(done), height=300)
with tab_started:
    started = workflows[["workflow_type", "project_name", "current_node", "current_handler", "approval_status", "start_time"]].head(18)
    render_filterable_table(to_display_df(started), height=300)
with tab_risk:
    remind = risks[["risk_type", "risk_level", "project_name", "trigger_reason", "responsible_person", "deadline", "current_status"]].head(20)
    render_filterable_table(to_display_df(remind), height=340)
with tab_quick:
    labels = ["新建立项", "新建采购申请", "新建费用报销", "新建付款申请", "新建安全检查", "新建质量检查", "上传项目资料"]
    cols = st.columns(4)
    for idx, label in enumerate(labels):
        if cols[idx % 4].button(label, use_container_width=True):
            st.success(f"已进入模拟入口：{label}")

render_business_note("工作台强调个人任务闭环：待办来自审批流，风险提醒来自项目风险中心，快捷入口用于模拟常见业务单据发起。")

