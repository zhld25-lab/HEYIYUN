"""审批中心 — 待办、已办、发起、全部、审批操作"""
from __future__ import annotations

import streamlit as st
import pandas as pd

import api_client as api
from utils import init_session, require_login, sidebar_nav, fmt_date, has_perm, WF_STATUS_LABEL, STEP_STATUS_ICON

st.set_page_config(page_title="审批中心 · ERP", page_icon="✅", layout="wide")
init_session()
require_login()
sidebar_nav()

st.markdown("## ✅ 审批中心")

ACTION_LABELS = {
    "submit": "提交", "approve": "审批通过", "reject": "驳回",
    "withdraw": "撤回", "urge": "催办", "transfer": "转办", "comment": "评论",
}

tab_pending, tab_done, tab_initiated, tab_all, tab_config = st.tabs(
    ["📌 我的待办", "✔️ 我的已办", "📤 我的发起", "📋 全部流程", "⚙️ 流程配置"]
)


def _wf_table(items: list, show_actions: bool = False, table_key: str = "wf") -> int | None:
    """Render workflow table, return selected workflow id or None."""
    if not items:
        st.info("暂无数据")
        return None

    rows = [{
        "ID": w["id"],
        "标题": w.get("title", ""),
        "流程类型": w.get("workflow_type", ""),
        "业务类型": w.get("business_type", ""),
        "状态": WF_STATUS_LABEL.get(w.get("status", ""), w.get("status", "")),
        "步骤": f"{w.get('current_step', 0)}/{w.get('total_steps', 0)}",
        "发起人": w.get("initiator_name", ""),
        "提交时间": fmt_date(w.get("submitted_at")),
        "完成时间": fmt_date(w.get("completed_at")) if w.get("completed_at") else "-",
    }]

    rows = [{
        "ID": w["id"],
        "标题": w.get("title", ""),
        "流程类型": w.get("workflow_type", ""),
        "状态": WF_STATUS_LABEL.get(w.get("status", ""), w.get("status", "")),
        "步骤": f"{w.get('current_step', 0)}/{w.get('total_steps', 0)}",
        "发起人": w.get("initiator_name", ""),
        "提交时间": fmt_date(w.get("submitted_at")),
    } for w in items]

    df = pd.DataFrame(rows)
    sel = st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True,
        height=min(400, len(items) * 40 + 60),
        on_select="rerun",
        selection_mode="single-row",
        key=f"df_{table_key}",
    )

    if sel and sel.selection.rows:
        return int(df.iloc[sel.selection.rows[0]]["ID"])
    return None


def _render_workflow_detail(wf: dict, show_action_buttons: bool = False):
    status = WF_STATUS_LABEL.get(wf.get("status", ""), wf.get("status", ""))
    st.markdown(f"### {wf.get('title')} · **{status}**")

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**流程类型：** {wf.get('workflow_type')}")
    col2.markdown(f"**业务类型：** {wf.get('business_type')} #{wf.get('business_id')}")
    col3.markdown(f"**发起人：** {wf.get('initiator_name')}")
    col1.markdown(f"**提交时间：** {fmt_date(wf.get('submitted_at'))}")
    col2.markdown(f"**完成时间：** {fmt_date(wf.get('completed_at')) if wf.get('completed_at') else '-'}")
    col3.markdown(f"**步骤：** {wf.get('current_step')}/{wf.get('total_steps')}")

    steps = wf.get("steps", [])
    if steps:
        st.markdown("---")
        st.markdown("**📋 审批步骤**")
        for s in steps:
            icon = STEP_STATUS_ICON.get(s.get("status", ""), "⚪")
            approver = s.get("approver_name") or f"[{s.get('approver_role', '')}角色待分配]"
            due = f" · 截止 {fmt_date(s.get('due_at'))}" if s.get("due_at") else ""
            acted = f" · {fmt_date(s.get('acted_at'))}" if s.get("acted_at") else ""
            comment = f"\n  > 💬 {s['comment']}" if s.get("comment") else ""
            st.markdown(
                f"{icon} **步骤{s['step_order']}：{s['step_name']}**  \n"
                f"  审批人：{approver}{due}{acted}{comment}"
            )

    actions = wf.get("actions", [])
    if actions:
        st.markdown("---")
        st.markdown("**📜 操作记录**")
        for a in reversed(actions):
            label = ACTION_LABELS.get(a.get("action", ""), a.get("action", ""))
            ts = (a.get("created_at") or "")[:16]
            comment = f" — {a['comment']}" if a.get("comment") else ""
            st.markdown(f"- `{ts}` **{a.get('actor_name', '')}** {label}{comment}")

    if show_action_buttons and wf.get("status") == "pending" and has_perm("workflow:approve"):
        st.markdown("---")
        st.markdown("**⚡ 审批操作**")
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        comment_input = st.text_area("审批意见", key=f"comment_{wf['id']}")

        if action_col1.button("✅ 通过", key=f"appr_{wf['id']}", type="primary"):
            r = api.post(f"/workflows/{wf['id']}/approve", {"comment": comment_input})
            if r and "_error" not in r:
                st.success("审批通过！")
                st.rerun()
            else:
                st.error(r.get("_error", "失败") if r else "失败")

        if action_col2.button("❌ 驳回", key=f"rej_{wf['id']}"):
            if not comment_input:
                st.warning("请填写驳回原因")
            else:
                r = api.post(f"/workflows/{wf['id']}/reject", {"comment": comment_input})
                if r and "_error" not in r:
                    st.error("已驳回")
                    st.rerun()
                else:
                    st.error(r.get("_error", "失败") if r else "失败")

        if action_col3.button("🔔 催办", key=f"urge_{wf['id']}"):
            r = api.post(f"/workflows/{wf['id']}/urge", {"comment": comment_input or "请尽快处理"})
            if r and "_error" not in r:
                st.info("催办通知已发送")
            else:
                st.error(r.get("_error", "失败") if r else "失败")

    if wf.get("status") == "pending" and has_perm("workflow:create"):
        user = st.session_state.get("user") or {}
        if wf.get("initiator_id") == user.get("id"):
            if st.button("↩️ 撤回", key=f"withdraw_{wf['id']}"):
                r = api.post(f"/workflows/{wf['id']}/withdraw", {})
                if r and "_error" not in r:
                    st.warning("审批已撤回")
                    st.rerun()
                else:
                    st.error(r.get("_error", "失败") if r else "失败")


# ── 我的待办 ───────────────────────────────────────────────────────────────

with tab_pending:
    with st.spinner("加载待办…"):
        pending = api.get("/workflows/my-pending") or []
    st.caption(f"待办：{len(pending)} 条")

    if pending:
        col_list, col_detail = st.columns([1.5, 2])
        with col_list:
            selected_id = _wf_table(pending, table_key="pending")
        with col_detail:
            if selected_id:
                with st.spinner("加载详情…"):
                    detail = api.get(f"/workflows/{selected_id}")
                if detail:
                    _render_workflow_detail(detail, show_action_buttons=True)
    else:
        st.info("🎉 暂无待办审批")

# ── 我的已办 ───────────────────────────────────────────────────────────────

with tab_done:
    with st.spinner("加载已办…"):
        done = api.get("/workflows/my-done") or []
    st.caption(f"已办：{len(done)} 条")
    selected_id = _wf_table(done, table_key="done")
    if selected_id:
        with st.spinner("加载详情…"):
            detail = api.get(f"/workflows/{selected_id}")
        if detail:
            with st.expander("流程详情", expanded=True):
                _render_workflow_detail(detail)

# ── 我的发起 ───────────────────────────────────────────────────────────────

with tab_initiated:
    with st.spinner("加载发起记录…"):
        initiated = api.get("/workflows/my-initiated") or []
    st.caption(f"发起：{len(initiated)} 条")

    col_l, col_r = st.columns([1.5, 2])
    with col_l:
        selected_id = _wf_table(initiated, table_key="initiated")
    with col_r:
        if selected_id:
            with st.spinner("加载详情…"):
                detail = api.get(f"/workflows/{selected_id}")
            if detail:
                _render_workflow_detail(detail)

# ── 全部流程 ───────────────────────────────────────────────────────────────

with tab_all:
    user_role = (st.session_state.get("user") or {}).get("role_code", "")
    if user_role not in ("admin", "general_manager"):
        st.info("全部流程仅限总经理和系统管理员查看")
    else:
        f1, f2 = st.columns(2)
        filter_status = f1.selectbox("状态筛选", ["全部", "draft", "pending", "approved", "rejected", "withdrawn"])
        filter_type = f2.selectbox("业务类型", ["全部", "project", "contract", "cost", "payment", "invoice"])

        params: dict = {}
        if filter_status != "全部":
            params["status"] = filter_status
        if filter_type != "全部":
            params["business_type"] = filter_type

        with st.spinner("加载所有流程…"):
            all_wfs = api.get("/workflows", params=params) or []
        st.caption(f"共 {len(all_wfs)} 条")

        col_l2, col_r2 = st.columns([1.5, 2])
        with col_l2:
            selected_id = _wf_table(all_wfs, table_key="all")
        with col_r2:
            if selected_id:
                with st.spinner("加载详情…"):
                    detail = api.get(f"/workflows/{selected_id}")
                if detail:
                    _render_workflow_detail(detail, show_action_buttons=True)

# ── 流程配置 ───────────────────────────────────────────────────────────────

with tab_config:
    st.markdown("### ⚙️ 流程模板配置")
    st.info("流程模板配置功能将在 Phase 4B 版本开放，当前使用内置默认步骤链。")
    st.markdown("""
**当前内置步骤链：**

| 流程类型 | 步骤链 |
|---------|-------|
| 项目立项审批 | 项目经理 → 财务负责人 → 总经理 |
| 合同审批 | 项目经理 → 财务负责人 → 总经理 |
| 付款审批 | 项目经理 → 财务负责人 → 总经理 |
| 成本审批 | 项目经理 → 财务负责人 |
| 发票审批 | 财务负责人 → 总经理 |
| 结算审批 | 项目经理 → 财务负责人 → 总经理 |
| 采购审批 | 项目经理 → 财务负责人 |
| 报销审批 | 项目经理 → 财务负责人 |
    """)
