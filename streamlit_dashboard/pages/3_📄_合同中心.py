"""合同中心 — 列表、新建、详情、审批"""
from __future__ import annotations

import streamlit as st
import pandas as pd

import api_client as api
from utils import init_session, require_login, sidebar_nav, fmt_wan, fmt_date, has_perm

st.set_page_config(page_title="合同中心 · ERP", page_icon="📄", layout="wide")
init_session()
require_login()
sidebar_nav()

CONTRACT_TYPES = ["承包合同", "分包合同", "采购合同", "设备租赁合同", "周材租赁合同", "其他"]
CONTRACT_STATUSES = ["执行中", "已完成", "已终止", "暂停"]
APPROVAL_STATUSES = ["待提交", "审批中", "已批准", "已驳回"]


def show_list():
    st.markdown("## 📄 合同中心")

    with st.expander("🔍 筛选", expanded=False):
        c1, c2, c3 = st.columns(3)
        f_name = c1.text_input("合同名称")
        f_type = c2.multiselect("合同类型", CONTRACT_TYPES)
        f_approval = c3.multiselect("审批状态", APPROVAL_STATUSES)

    with st.spinner("加载合同…"):
        data = api.get("/contracts", params={"page_size": 200}) or {}
    items = data.get("items", []) if isinstance(data, dict) else []

    if f_name:
        items = [c for c in items if f_name.lower() in c.get("contract_name", "").lower()]
    if f_type:
        items = [c for c in items if c.get("contract_type") in f_type]
    if f_approval:
        items = [c for c in items if c.get("approval_status") in f_approval]

    btn1, btn2, _ = st.columns([1, 1, 8])
    if has_perm("contract:create") and btn1.button("➕ 新建合同", type="primary"):
        st.session_state["contract_view"] = "create"
        st.rerun()
    btn2.button("🔄 刷新", on_click=st.rerun)

    st.caption(f"共 {len(items)} 份合同")
    if not items:
        st.info("暂无合同数据")
        return

    rows = [{
        "ID": c["id"],
        "合同编号": c.get("contract_code", ""),
        "合同名称": c.get("contract_name", ""),
        "类型": c.get("contract_type", ""),
        "合同金额": fmt_wan(c.get("contract_amount")),
        "已收": fmt_wan(c.get("received_amount")),
        "已付": fmt_wan(c.get("paid_amount")),
        "合同状态": c.get("contract_status", ""),
        "审批状态": c.get("approval_status", ""),
        "签订日期": fmt_date(c.get("signed_date")),
    } for c in items]
    df = pd.DataFrame(rows)

    sel = st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True, height=400,
        on_select="rerun", selection_mode="single-row",
    )

    if sel and sel.selection.rows:
        cid = df.iloc[sel.selection.rows[0]]["ID"]
        selected = next((c for c in items if c["id"] == cid), {})

        col_v, col_e, col_appr, col_del = st.columns(4)
        if col_v.button("👁 详情"):
            st.session_state["contract_view"] = "detail"
            st.session_state["contract_id"] = cid
            st.rerun()
        if has_perm("contract:update") and col_e.button("✏️ 编辑"):
            st.session_state["contract_view"] = "edit"
            st.session_state["contract_id"] = cid
            st.rerun()
        # Submit approval button
        appr_status = selected.get("approval_status", "")
        if has_perm("workflow:create") and appr_status in ("待提交", "已驳回", ""):
            if col_appr.button("🚀 提交审批"):
                r = api.post(f"/contracts/{cid}/submit-approval")
                if r and "_error" not in r:
                    st.success("合同审批已提交！")
                    st.rerun()
                else:
                    st.error(r.get("_error", "提交失败") if r else "失败")
        elif appr_status == "审批中":
            col_appr.info("审批中")
        elif appr_status == "已批准":
            col_appr.success("已批准 ✅")

        if has_perm("contract:delete") and col_del.button("🗑️ 删除"):
            r = api.delete(f"/contracts/{cid}")
            if r is not None:
                st.success("已删除")
                st.rerun()


def show_detail(contract_id: int):
    with st.spinner("加载合同…"):
        c = api.get(f"/contracts/{contract_id}")
        workflows = api.get(f"/workflows/business/contract/{contract_id}") or []

    if not c:
        st.error("合同不存在")
        return

    st.markdown(f"## 📄 {c.get('contract_name')}")
    if st.button("← 返回"):
        st.session_state["contract_view"] = "list"
        st.rerun()

    tab_info, tab_approval = st.tabs(["合同信息", "审批记录"])

    with tab_info:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**合同编号：** {c.get('contract_code')}")
            st.write(f"**合同类型：** {c.get('contract_type')}")
            st.write(f"**甲方：** {c.get('party_a', '-')}")
            st.write(f"**乙方：** {c.get('party_b', '-')}")
            st.write(f"**签订日期：** {fmt_date(c.get('signed_date'))}")
        with col2:
            st.write(f"**合同状态：** {c.get('contract_status')}")
            st.write(f"**审批状态：** {c.get('approval_status')}")
            st.write(f"**归档状态：** {c.get('archive_status')}")
        st.markdown("**金额**")
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("合同金额", fmt_wan(c.get("contract_amount")))
        a2.metric("已收款", fmt_wan(c.get("received_amount")))
        a3.metric("已付款", fmt_wan(c.get("paid_amount")))
        a4.metric("结算金额", fmt_wan(c.get("settlement_amount")))
        if c.get("remarks"):
            st.write(f"**备注：** {c['remarks']}")

    with tab_approval:
        appr_status = c.get("approval_status", "")
        if has_perm("workflow:create") and appr_status in ("待提交", "已驳回", ""):
            if st.button("🚀 提交合同审批", type="primary"):
                r = api.post(f"/contracts/{contract_id}/submit-approval")
                if r and "_error" not in r:
                    st.success("审批已提交！")
                    st.rerun()
                else:
                    st.error(r.get("_error", "提交失败") if r else "失败")

        if workflows:
            for w in workflows:
                _render_workflow_card(w)
        else:
            st.info("暂无审批记录")


def _render_workflow_card(w: dict):
    status_label = {"draft": "草稿", "pending": "⏳ 审批中", "approved": "✅ 已批准",
                    "rejected": "❌ 已驳回", "withdrawn": "↩️ 已撤回"}.get(w.get("status", ""), w.get("status"))
    with st.expander(f"**{w.get('title')}** · {status_label} · 步骤 {w.get('current_step')}/{w.get('total_steps')}"):
        steps = w.get("steps", [])
        for s in steps:
            icon = {"approved": "✅", "rejected": "❌", "pending": "🔵", "waiting": "⚪"}.get(s.get("status", ""), "⚪")
            st.markdown(
                f"{icon} 步骤{s['step_order']}：{s['step_name']} "
                f"— {s.get('approver_name') or s.get('approver_role', '')} "
                f"{'· ' + s['comment'] if s.get('comment') else ''}"
            )


def show_form(contract_id: int | None = None):
    is_edit = contract_id is not None
    st.markdown(f"## {'✏️ 编辑合同' if is_edit else '➕ 新建合同'}")

    existing = api.get(f"/contracts/{contract_id}") if is_edit else {}
    projects = (api.get("/projects", params={"page_size": 100}) or {}).get("items", [])
    project_options = {p["id"]: f"{p['project_code']} {p['project_name']}" for p in projects}

    if st.button("← 返回"):
        st.session_state["contract_view"] = "list"
        st.rerun()

    with st.form("contract_form"):
        c1, c2 = st.columns(2)
        contract_code = c1.text_input("合同编号 *", value=existing.get("contract_code", ""))
        contract_name = c2.text_input("合同名称 *", value=existing.get("contract_name", ""))

        c3, c4, c5 = st.columns(3)
        contract_type = c3.selectbox("合同类型", CONTRACT_TYPES,
                                      index=CONTRACT_TYPES.index(existing["contract_type"])
                                      if existing.get("contract_type") in CONTRACT_TYPES else 0)
        proj_ids = list(project_options.keys())
        existing_proj_idx = proj_ids.index(existing["project_id"]) if existing.get("project_id") in proj_ids else 0
        selected_proj_id = c4.selectbox("所属项目 *", proj_ids,
                                         index=existing_proj_idx,
                                         format_func=lambda x: project_options.get(x, str(x)))
        import datetime
        signed_date = c5.date_input("签订日期",
                                     value=datetime.date.fromisoformat(existing["signed_date"])
                                     if existing.get("signed_date") else datetime.date.today())

        p1, p2 = st.columns(2)
        party_a = p1.text_input("甲方", value=existing.get("party_a", ""))
        party_b = p2.text_input("乙方", value=existing.get("party_b", ""))

        a1, a2 = st.columns(2)
        contract_amount = a1.number_input("合同金额（元）",
                                           value=float(existing.get("contract_amount") or 0),
                                           min_value=0.0, step=10000.0)
        settlement_amount = a2.number_input("结算金额（元）",
                                             value=float(existing.get("settlement_amount") or 0),
                                             min_value=0.0, step=10000.0)

        remarks = st.text_area("备注", value=existing.get("remarks", ""))
        submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)

    if submitted:
        if not contract_code or not contract_name:
            st.error("合同编号和合同名称为必填")
            return
        payload = {
            "contract_code": contract_code,
            "contract_name": contract_name,
            "contract_type": contract_type,
            "project_id": selected_proj_id,
            "signed_date": signed_date.isoformat(),
            "party_a": party_a,
            "party_b": party_b,
            "contract_amount": contract_amount,
            "settlement_amount": settlement_amount,
            "remarks": remarks,
        }
        with st.spinner("保存中…"):
            result = api.put(f"/contracts/{contract_id}", payload) if is_edit \
                else api.post_create("/contracts", payload)
        if result and "_error" not in result:
            st.success("保存成功！")
            st.session_state["contract_view"] = "list"
            st.rerun()
        else:
            st.error(f"保存失败：{result.get('_error', '') if result else '请求失败'}")


# ── Router ─────────────────────────────────────────────────────────────────
view = st.session_state.get("contract_view", "list")
if view == "list":
    show_list()
elif view == "detail":
    show_detail(st.session_state.get("contract_id"))
elif view == "create":
    show_form()
elif view == "edit":
    show_form(st.session_state.get("contract_id"))
