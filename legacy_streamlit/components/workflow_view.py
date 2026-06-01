from __future__ import annotations

import streamlit as st

from services.workflow_service import simulate_approve, simulate_reject


def render_workflow_timeline(trace: str) -> None:
    nodes = [node.strip() for node in str(trace).split(">") if node.strip()]
    if not nodes:
        st.info("暂无流程轨迹。")
        return
    for idx, node in enumerate(nodes, start=1):
        st.markdown(f"**{idx}. {node}**")


def render_workflow_status(workflow: dict) -> None:
    cols = st.columns(4)
    cols[0].metric("流程状态", workflow.get("approval_status", "-"))
    cols[1].metric("当前节点", workflow.get("current_node", "-"))
    cols[2].metric("当前处理人", workflow.get("current_handler", "-"))
    cols[3].metric("是否超时", "是" if workflow.get("is_overdue") else "否")
    render_workflow_timeline(workflow.get("trace", ""))


def render_workflow_actions(workflow_id: str) -> None:
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("通过", key=f"approve_{workflow_id}", use_container_width=True):
        st.success(simulate_approve(workflow_id)["message"])
    if col2.button("驳回", key=f"reject_{workflow_id}", use_container_width=True):
        st.warning(simulate_reject(workflow_id)["message"])
    if col3.button("转交", key=f"transfer_{workflow_id}", use_container_width=True):
        st.info("已模拟转交给下一处理人。")
    if col4.button("催办", key=f"remind_{workflow_id}", use_container_width=True):
        st.success("已模拟发送催办消息。")

