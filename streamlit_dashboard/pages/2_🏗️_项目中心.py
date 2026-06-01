"""项目中心 — 列表、新建、编辑、详情"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

import api_client as api
from utils import init_session, require_login, sidebar_nav, fmt_wan, fmt_pct, fmt_date, has_perm

st.set_page_config(page_title="项目中心 · ERP", page_icon="🏗️", layout="wide")
init_session()
require_login()
sidebar_nav()

# ── Constants ──────────────────────────────────────────────────────────────
PROJECT_TYPES = ["10kV配电工程", "35kV配电工程", "110kV输变电工程", "220kV输变电工程",
                 "500kV输变电工程", "光伏并网工程", "风电并网工程", "配网改造工程", "其他"]
VOLTAGE_LEVELS = ["10kV", "35kV", "110kV", "220kV", "500kV", "其他"]
PROJECT_STATUSES = ["立项", "报装中", "施工中", "验收中", "已完工", "已竣工", "暂停", "已取消"]
RISK_LEVELS = ["低", "中", "高"]


def _get_pm_options() -> dict:
    users = api.get("/users") or []
    return {u["id"]: u["full_name"] for u in users}


# ── List ───────────────────────────────────────────────────────────────────

def show_list():
    st.markdown("## 🏗️ 项目中心")

    # Filters
    with st.expander("🔍 筛选", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        f_name = c1.text_input("项目名称")
        f_status = c2.multiselect("项目状态", PROJECT_STATUSES)
        f_risk = c3.multiselect("风险等级", RISK_LEVELS)
        f_type = c4.multiselect("项目类型", PROJECT_TYPES)

    params: dict = {"page_size": 200}
    if f_name:
        params["project_name"] = f_name

    with st.spinner("加载项目…"):
        data = api.get("/projects", params=params) or {}
    items = data.get("items", []) if isinstance(data, dict) else []

    # Client-side filters
    if f_status:
        items = [p for p in items if p.get("project_status") in f_status]
    if f_risk:
        items = [p for p in items if p.get("risk_level") in f_risk]
    if f_type:
        items = [p for p in items if p.get("project_type") in f_type]

    # Action buttons
    btn_col1, btn_col2, _ = st.columns([1, 1, 8])
    if btn_col1.button("➕ 新建项目", type="primary"):
        st.session_state["project_view"] = "create"
        st.rerun()
    if btn_col2.button("🔄 刷新"):
        st.rerun()

    st.caption(f"共 {len(items)} 个项目")

    if not items:
        st.info("暂无项目数据")
        return

    # KPI row
    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric("项目数", len(items))
    amounts = [float(p["contract_amount"]) for p in items if p.get("contract_amount") not in (None, "***")]
    kc2.metric("合同额合计", fmt_wan(sum(amounts)) if amounts else "***")
    progresses = [float(p["production_progress"]) for p in items
                  if p.get("production_progress") not in (None, "***")]
    kc3.metric("平均施工进度", f"{sum(progresses)/len(progresses)*100:.1f}%" if progresses else "-")
    kc4.metric("高风险项目", sum(1 for p in items if p.get("risk_level") == "高"))

    # Table
    rows = [{
        "ID": p["id"],
        "编号": p.get("project_code", ""),
        "项目名称": p.get("project_name", ""),
        "类型": p.get("project_type", ""),
        "状态": p.get("project_status", ""),
        "风险": p.get("risk_level", ""),
        "合同额": fmt_wan(p.get("contract_amount")),
        "实际成本": fmt_wan(p.get("actual_cost")),
        "回款": fmt_wan(p.get("received_amount")),
        "施工进度": fmt_pct(p.get("production_progress")),
        "回款进度": fmt_pct(p.get("collection_progress")),
        "计划完工": fmt_date(p.get("planned_end_date")),
    } for p in items]
    df = pd.DataFrame(rows)

    sel = st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True,
        height=380,
        on_select="rerun",
        selection_mode="single-row",
    )

    if sel and sel.selection.rows:
        selected_id = df.iloc[sel.selection.rows[0]]["ID"]
        col_v, col_e, col_del = st.columns([1, 1, 1])
        if col_v.button("👁 查看详情"):
            st.session_state["project_view"] = "detail"
            st.session_state["project_id"] = selected_id
            st.rerun()
        if has_perm("project:update") and col_e.button("✏️ 编辑"):
            st.session_state["project_view"] = "edit"
            st.session_state["project_id"] = selected_id
            st.rerun()
        if has_perm("project:delete") and col_del.button("🗑️ 删除", type="primary"):
            if st.session_state.get(f"confirm_delete_{selected_id}"):
                result = api.delete(f"/projects/{selected_id}")
                st.success("项目已删除")
                st.session_state.pop(f"confirm_delete_{selected_id}", None)
                st.rerun()
            else:
                st.session_state[f"confirm_delete_{selected_id}"] = True
                st.warning("再次点击删除确认。")

    # Scatter chart
    chart_data = [p for p in items if p.get("production_progress") not in (None, "***")
                  and p.get("collection_progress") not in (None, "***")]
    if chart_data:
        with st.expander("📈 施工进度 vs 回款进度", expanded=False):
            df_sc = pd.DataFrame([{
                "project_name": p["project_name"],
                "施工进度(%)": float(p["production_progress"]) * 100,
                "回款进度(%)": float(p["collection_progress"]) * 100,
                "风险": p.get("risk_level", "低"),
            } for p in chart_data])
            fig = px.scatter(df_sc, x="施工进度(%)", y="回款进度(%)",
                             color="风险", hover_name="project_name",
                             color_discrete_map={"高": "#ff4d4f", "中": "#faad14", "低": "#52c41a"},
                             range_x=[0, 110], range_y=[0, 110])
            fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100,
                          line=dict(color="gray", dash="dash"))
            fig.update_layout(height=380, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)


# ── Detail ─────────────────────────────────────────────────────────────────

def show_detail(project_id: int):
    with st.spinner("加载项目详情…"):
        p = api.get(f"/projects/{project_id}")
        finance = api.get(f"/projects/{project_id}/finance-summary")
        workflows = api.get(f"/projects/{project_id}/workflows") or []

    if not p:
        st.error("项目不存在")
        return

    st.markdown(f"## 🏗️ {p.get('project_name')}")
    st.caption(f"编号：{p.get('project_code')}")

    bc1, bc2 = st.columns([1, 9])
    if bc1.button("← 返回列表"):
        st.session_state["project_view"] = "list"
        st.rerun()
    if has_perm("project:update") and bc2.button("✏️ 编辑"):
        st.session_state["project_view"] = "edit"
        st.session_state["project_id"] = project_id
        st.rerun()

    tab_basic, tab_finance, tab_approval, tab_audit = st.tabs(
        ["基本信息", "财务汇总", "审批记录", "操作日志"]
    )

    with tab_basic:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**基本信息**")
            st.write(f"项目类型：{p.get('project_type', '-')}")
            st.write(f"电压等级：{p.get('voltage_level', '-')}")
            st.write(f"项目状态：{p.get('project_status', '-')}")
            st.write(f"风险等级：{p.get('risk_level', '-')}")
            st.write(f"所在区域：{p.get('region', '-')}")
        with c2:
            st.markdown("**时间计划**")
            st.write(f"计划开工：{fmt_date(p.get('planned_start_date'))}")
            st.write(f"计划完工：{fmt_date(p.get('planned_end_date'))}")
            st.write(f"实际开工：{fmt_date(p.get('actual_start_date'))}")
            st.write(f"实际完工：{fmt_date(p.get('actual_end_date'))}")

        st.markdown("**参建单位**")
        st.write(f"建设单位：{p.get('owner_unit', '-')} | 施工单位：{p.get('construction_unit', '-')}")
        st.write(f"设计单位：{p.get('design_unit', '-')} | 监理单位：{p.get('supervision_unit', '-')}")

        st.markdown("**进度**")
        pr1, pr2, pr3, pr4 = st.columns(4)
        pr1.metric("施工进度", fmt_pct(p.get("production_progress")))
        pr2.metric("回款进度", fmt_pct(p.get("collection_progress")))
        pr3.metric("成本率", fmt_pct(p.get("cost_ratio")))
        pr4.metric("资料完成率", fmt_pct(p.get("document_completion_rate")))

    with tab_finance:
        if finance:
            fa, fb, fc, fd = st.columns(4)
            fa.metric("合同额", fmt_wan(finance.get("contract_amount")))
            fb.metric("目标成本", fmt_wan(finance.get("target_cost")))
            fc.metric("实际成本", fmt_wan(finance.get("actual_cost")))
            fd.metric("利润", fmt_wan(finance.get("profit")))
            fe, ff, fg, fh = st.columns(4)
            fe.metric("回款", fmt_wan(finance.get("received_amount")))
            ff.metric("付款", fmt_wan(finance.get("paid_amount")))
            fg.metric("应收款", fmt_wan(finance.get("receivable_amount")))
            fh.metric("应付款", fmt_wan(finance.get("payable_amount")))
        else:
            st.info("暂无财务数据或权限不足")

    with tab_approval:
        if has_perm("workflow:create"):
            if st.button("🚀 提交立项审批", type="primary"):
                r = api.post(f"/projects/{project_id}/submit-approval")
                if r and "_error" not in r:
                    st.success("审批已提交！")
                    st.rerun()
                else:
                    st.error(r.get("_error", "提交失败") if r else "提交失败")

        if workflows:
            wf_rows = [{
                "ID": w["id"],
                "标题": w["title"],
                "类型": w["workflow_type"],
                "状态": {"draft": "草稿", "pending": "审批中", "approved": "✅ 已批准",
                         "rejected": "❌ 已驳回", "withdrawn": "↩️ 已撤回"}.get(w["status"], w["status"]),
                "步骤": f"{w['current_step']}/{w['total_steps']}",
                "发起人": w.get("initiator_name", ""),
                "提交时间": fmt_date(w.get("submitted_at")),
            } for w in workflows]
            st.dataframe(pd.DataFrame(wf_rows).drop(columns=["ID"]),
                         use_container_width=True)
        else:
            st.info("暂无审批记录")

    with tab_audit:
        audit = api.get(f"/system/audit-logs?resource_type=project&resource_id={project_id}") or {}
        logs = audit.get("items", []) if isinstance(audit, dict) else []
        if logs:
            df_log = pd.DataFrame([{
                "时间": l["created_at"][:16] if l.get("created_at") else "-",
                "操作人": l.get("username", ""),
                "操作": l.get("action", ""),
                "IP": l.get("ip_address", ""),
            } for l in logs])
            st.dataframe(df_log, use_container_width=True)
        else:
            st.info("暂无操作日志")


# ── Form (create / edit) ───────────────────────────────────────────────────

def show_form(project_id: int | None = None):
    is_edit = project_id is not None
    st.markdown(f"## {'✏️ 编辑项目' if is_edit else '➕ 新建项目'}")

    existing = api.get(f"/projects/{project_id}") if is_edit else {}
    if is_edit and not existing:
        st.error("项目不存在")
        return

    if st.button("← 返回列表"):
        st.session_state["project_view"] = "list"
        st.rerun()

    with st.form("project_form"):
        st.markdown("**基本信息**")
        c1, c2 = st.columns(2)
        project_code = c1.text_input("项目编号 *", value=existing.get("project_code", ""))
        project_name = c2.text_input("项目名称 *", value=existing.get("project_name", ""))

        c3, c4, c5 = st.columns(3)
        project_type = c3.selectbox("项目类型", PROJECT_TYPES,
                                     index=PROJECT_TYPES.index(existing["project_type"])
                                     if existing.get("project_type") in PROJECT_TYPES else 0)
        voltage_level = c4.selectbox("电压等级", VOLTAGE_LEVELS,
                                      index=VOLTAGE_LEVELS.index(existing["voltage_level"])
                                      if existing.get("voltage_level") in VOLTAGE_LEVELS else 0)
        project_status = c5.selectbox("项目状态", PROJECT_STATUSES,
                                       index=PROJECT_STATUSES.index(existing["project_status"])
                                       if existing.get("project_status") in PROJECT_STATUSES else 1)

        st.markdown("**时间计划**")
        d1, d2 = st.columns(2)
        import datetime
        planned_start = d1.date_input("计划开工日期",
                                       value=datetime.date.fromisoformat(existing["planned_start_date"])
                                       if existing.get("planned_start_date") else datetime.date.today())
        planned_end = d2.date_input("计划完工日期",
                                     value=datetime.date.fromisoformat(existing["planned_end_date"])
                                     if existing.get("planned_end_date") else datetime.date.today())

        st.markdown("**参建单位**")
        u1, u2 = st.columns(2)
        owner_unit = u1.text_input("建设单位", value=existing.get("owner_unit", ""))
        construction_unit = u2.text_input("施工单位", value=existing.get("construction_unit", ""))

        st.markdown("**进度与风险**")
        p1, p2, p3 = st.columns(3)
        production_progress = p1.slider("施工进度", 0.0, 1.0,
                                         value=float(existing.get("production_progress") or 0),
                                         step=0.01, format="%.0f%%")
        risk_level = p2.selectbox("风险等级", RISK_LEVELS,
                                   index=RISK_LEVELS.index(existing.get("risk_level", "低"))
                                   if existing.get("risk_level") in RISK_LEVELS else 0)
        region = p3.text_input("所在区域", value=existing.get("region", ""))

        st.markdown("**金额（元）**")
        a1, a2 = st.columns(2)
        contract_amount = a1.number_input("合同金额", value=float(existing.get("contract_amount") or 0),
                                           min_value=0.0, step=10000.0)
        target_cost = a2.number_input("目标成本", value=float(existing.get("target_cost") or 0),
                                       min_value=0.0, step=10000.0)

        remarks = st.text_area("备注", value=existing.get("remarks", ""))

        submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)

    if submitted:
        if not project_code or not project_name:
            st.error("项目编号和项目名称为必填项")
            return
        payload = {
            "project_code": project_code,
            "project_name": project_name,
            "project_type": project_type,
            "voltage_level": voltage_level,
            "project_status": project_status,
            "planned_start_date": planned_start.isoformat(),
            "planned_end_date": planned_end.isoformat(),
            "owner_unit": owner_unit,
            "construction_unit": construction_unit,
            "production_progress": production_progress,
            "risk_level": risk_level,
            "region": region,
            "contract_amount": contract_amount,
            "target_cost": target_cost,
            "remarks": remarks,
        }
        with st.spinner("保存中…"):
            if is_edit:
                result = api.put(f"/projects/{project_id}", payload)
            else:
                result = api.post_create("/projects", payload)

        if result and "_error" not in result:
            st.success("保存成功！")
            st.session_state["project_view"] = "list"
            st.rerun()
        else:
            st.error(f"保存失败：{result.get('_error', '未知错误') if result else '请求失败'}")


# ── Router ─────────────────────────────────────────────────────────────────

view = st.session_state.get("project_view", "list")

if view == "list":
    show_list()
elif view == "detail":
    show_detail(st.session_state.get("project_id"))
elif view == "create":
    show_form()
elif view == "edit":
    show_form(project_id=st.session_state.get("project_id"))
