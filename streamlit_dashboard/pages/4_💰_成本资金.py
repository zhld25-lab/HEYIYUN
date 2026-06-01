"""成本资金中心 — 成本/付款/回款/发票台账"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import datetime

import api_client as api
from utils import init_session, require_login, sidebar_nav, fmt_wan, fmt_date, has_perm

st.set_page_config(page_title="成本资金 · ERP", page_icon="💰", layout="wide")
init_session()
require_login()
sidebar_nav()

st.markdown("## 💰 成本资金中心")

COST_TYPES = ["人工费", "材料费", "机械费", "分包费", "设备费", "周材租赁费",
              "管理费", "安全文明费", "临时设施费", "其他"]
PAYMENT_STATUSES = ["待付款", "部分付款", "已付款", "已取消"]
INVOICE_TYPES = ["增值税专用发票", "增值税普通发票", "收据", "其他"]


def _get_project_options() -> dict:
    data = api.get("/projects", params={"page_size": 100}) or {}
    items = data.get("items", []) if isinstance(data, dict) else []
    return {p["id"]: f"{p['project_code']} {p['project_name']}" for p in items}


def _get_contract_options(project_id: int | None = None) -> dict:
    path = f"/projects/{project_id}/contracts" if project_id else "/contracts"
    data = api.get(path, params={"page_size": 200}) or {}
    items = data.get("items", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    return {c["id"]: f"{c['contract_code']} {c['contract_name']}" for c in items}


tab_cost, tab_payment, tab_receipt, tab_invoice = st.tabs(
    ["📋 成本台账", "💳 付款管理", "💵 回款管理", "🧾 发票管理"]
)

# ── 成本台账 ───────────────────────────────────────────────────────────────

with tab_cost:
    with st.spinner("加载成本数据…"):
        data = api.get("/costs", params={"page_size": 200}) or {}
    items = data.get("items", []) if isinstance(data, dict) else []

    c1, c2, _ = st.columns([1, 1, 8])
    if has_perm("finance:edit") and c1.button("➕ 新增成本", key="add_cost", type="primary"):
        st.session_state["cost_form"] = True
    c2.button("🔄", key="ref_cost", on_click=st.rerun)

    if st.session_state.get("cost_form"):
        project_opts = _get_project_options()
        with st.form("cost_form"):
            st.markdown("**新增成本记录**")
            fc1, fc2 = st.columns(2)
            cost_code = fc1.text_input("成本编号 *")
            cost_type = fc2.selectbox("成本类型", COST_TYPES)
            proj_ids = list(project_opts.keys())
            proj_id = fc1.selectbox("所属项目 *", proj_ids,
                                     format_func=lambda x: project_opts.get(x, str(x)))
            supplier = fc2.text_input("供应商")
            amount = fc1.number_input("金额（元）", min_value=0.0, step=1000.0)
            occurred_date = fc2.date_input("发生日期", value=datetime.date.today())
            remarks = st.text_area("备注")
            ok = st.form_submit_button("保存", type="primary")
        if ok:
            if not cost_code:
                st.error("成本编号为必填")
            else:
                r = api.post_create("/costs", {
                    "cost_code": cost_code, "cost_type": cost_type,
                    "project_id": proj_id, "supplier_name": supplier,
                    "amount": amount, "occurred_date": occurred_date.isoformat(),
                    "remarks": remarks,
                })
                if r and "_error" not in r:
                    st.success("成本记录已新增！")
                    st.session_state["cost_form"] = False
                    st.rerun()
                else:
                    st.error(r.get("_error", "失败") if r else "失败")

    if items:
        st.caption(f"共 {len(items)} 条成本记录")
        rows = [{
            "ID": c["id"],
            "成本编号": c.get("cost_code", ""),
            "成本类型": c.get("cost_type", ""),
            "供应商": c.get("supplier_name", ""),
            "金额": fmt_wan(c.get("amount")),
            "发生日期": fmt_date(c.get("occurred_date")),
            "审批状态": c.get("approval_status", ""),
            "付款状态": c.get("payment_status", ""),
        } for c in items]
        df = pd.DataFrame(rows)
        sel = st.dataframe(df.drop(columns=["ID"]), use_container_width=True, height=350,
                           on_select="rerun", selection_mode="single-row")
        if sel and sel.selection.rows:
            cid = df.iloc[sel.selection.rows[0]]["ID"]
            selected = next((c for c in items if c["id"] == cid), {})
            col_appr, col_del = st.columns(2)
            appr_st = selected.get("approval_status", "")
            if has_perm("workflow:create") and appr_st in ("待提交", "已驳回", ""):
                if col_appr.button("🚀 提交成本审批", key="cost_appr"):
                    r = api.post(f"/costs/{cid}/submit-approval")
                    st.success("已提交！") if r and "_error" not in r else st.error("失败")
                    st.rerun()
            if has_perm("finance:delete") and col_del.button("🗑️ 删除", key="cost_del"):
                api.delete(f"/costs/{cid}")
                st.success("已删除")
                st.rerun()
    else:
        st.info("暂无成本记录")

# ── 付款管理 ───────────────────────────────────────────────────────────────

with tab_payment:
    with st.spinner("加载付款数据…"):
        data = api.get("/payments", params={"page_size": 200}) or {}
    items = data.get("items", []) if isinstance(data, dict) else []

    p1, p2, _ = st.columns([1, 1, 8])
    if has_perm("finance:edit") and p1.button("➕ 新增付款", key="add_pay", type="primary"):
        st.session_state["pay_form"] = True
    p2.button("🔄", key="ref_pay", on_click=st.rerun)

    if st.session_state.get("pay_form"):
        project_opts = _get_project_options()
        with st.form("pay_form"):
            st.markdown("**新增付款记录**")
            fp1, fp2 = st.columns(2)
            payment_code = fp1.text_input("付款编号 *")
            proj_ids = list(project_opts.keys())
            proj_id = fp2.selectbox("所属项目 *", proj_ids,
                                     format_func=lambda x: project_opts.get(x, str(x)))
            payee = fp1.text_input("收款方")
            requested = fp2.number_input("申请金额（元）", min_value=0.0, step=1000.0)
            paid = fp1.number_input("实付金额（元）", min_value=0.0, step=1000.0)
            pay_date = fp2.date_input("付款日期", value=datetime.date.today())
            remarks = st.text_area("备注")
            ok = st.form_submit_button("保存", type="primary")
        if ok:
            if not payment_code:
                st.error("付款编号为必填")
            else:
                r = api.post_create("/payments", {
                    "payment_code": payment_code, "project_id": proj_id,
                    "payee_name": payee, "requested_amount": requested,
                    "paid_amount": paid, "payment_date": pay_date.isoformat(),
                    "remarks": remarks,
                })
                if r and "_error" not in r:
                    st.success("付款记录已新增！")
                    st.session_state["pay_form"] = False
                    st.rerun()
                else:
                    st.error(r.get("_error", "失败") if r else "失败")

    if items:
        st.caption(f"共 {len(items)} 条付款记录")
        rows = [{
            "ID": p["id"],
            "付款编号": p.get("payment_code", ""),
            "收款方": p.get("payee_name", ""),
            "申请金额": fmt_wan(p.get("requested_amount")),
            "实付金额": fmt_wan(p.get("paid_amount")),
            "付款日期": fmt_date(p.get("payment_date")),
            "付款状态": p.get("payment_status", ""),
            "审批状态": p.get("approval_status", ""),
        } for p in items]
        df = pd.DataFrame(rows)
        sel = st.dataframe(df.drop(columns=["ID"]), use_container_width=True, height=350,
                           on_select="rerun", selection_mode="single-row")
        if sel and sel.selection.rows:
            pid = df.iloc[sel.selection.rows[0]]["ID"]
            selected = next((p for p in items if p["id"] == pid), {})
            col_appr, col_del = st.columns(2)
            appr_st = selected.get("approval_status", "")
            if has_perm("workflow:create") and appr_st in ("待提交", "已驳回", ""):
                if col_appr.button("🚀 提交付款审批", key="pay_appr"):
                    r = api.post(f"/payments/{pid}/submit-approval")
                    st.success("已提交！") if r and "_error" not in r else st.error("失败")
                    st.rerun()
            if has_perm("finance:delete") and col_del.button("🗑️ 删除", key="pay_del"):
                api.delete(f"/payments/{pid}")
                st.success("已删除")
                st.rerun()
    else:
        st.info("暂无付款记录")

# ── 回款管理 ───────────────────────────────────────────────────────────────

with tab_receipt:
    with st.spinner("加载回款数据…"):
        data = api.get("/receipts", params={"page_size": 200}) or {}
    items = data.get("items", []) if isinstance(data, dict) else []

    r1, r2, _ = st.columns([1, 1, 8])
    if has_perm("finance:edit") and r1.button("➕ 新增回款", key="add_rec", type="primary"):
        st.session_state["rec_form"] = True
    r2.button("🔄", key="ref_rec", on_click=st.rerun)

    if st.session_state.get("rec_form"):
        project_opts = _get_project_options()
        with st.form("rec_form"):
            st.markdown("**新增回款记录**")
            rr1, rr2 = st.columns(2)
            receipt_code = rr1.text_input("回款编号 *")
            proj_ids = list(project_opts.keys())
            proj_id = rr2.selectbox("所属项目 *", proj_ids,
                                     format_func=lambda x: project_opts.get(x, str(x)))
            payer = rr1.text_input("付款方")
            receipt_amount = rr2.number_input("回款金额（元）", min_value=0.0, step=1000.0)
            receipt_date = rr1.date_input("回款日期", value=datetime.date.today())
            planned_date = rr2.date_input("计划回款日期", value=datetime.date.today())
            remarks = st.text_area("备注")
            ok = st.form_submit_button("保存", type="primary")
        if ok:
            if not receipt_code:
                st.error("回款编号为必填")
            else:
                r = api.post_create("/receipts", {
                    "receipt_code": receipt_code, "project_id": proj_id,
                    "payer_name": payer, "receipt_amount": receipt_amount,
                    "receipt_date": receipt_date.isoformat(),
                    "planned_receipt_date": planned_date.isoformat(),
                    "remarks": remarks,
                })
                if r and "_error" not in r:
                    st.success("回款记录已新增！")
                    st.session_state["rec_form"] = False
                    st.rerun()
                else:
                    st.error(r.get("_error", "失败") if r else "失败")

    if items:
        st.caption(f"共 {len(items)} 条回款记录")
        rows = [{
            "ID": i["id"],
            "回款编号": i.get("receipt_code", ""),
            "付款方": i.get("payer_name", ""),
            "回款金额": fmt_wan(i.get("receipt_amount")),
            "回款日期": fmt_date(i.get("receipt_date")),
            "计划回款日": fmt_date(i.get("planned_receipt_date")),
            "是否逾期": "是" if i.get("is_overdue") else "否",
        } for i in items]
        st.dataframe(pd.DataFrame(rows).drop(columns=["ID"]), use_container_width=True, height=350)
    else:
        st.info("暂无回款记录")

# ── 发票管理 ───────────────────────────────────────────────────────────────

with tab_invoice:
    with st.spinner("加载发票数据…"):
        data = api.get("/invoices", params={"page_size": 200}) or {}
    items = data.get("items", []) if isinstance(data, dict) else []

    iv1, iv2, _ = st.columns([1, 1, 8])
    if has_perm("finance:edit") and iv1.button("➕ 新增发票", key="add_inv", type="primary"):
        st.session_state["inv_form"] = True
    iv2.button("🔄", key="ref_inv", on_click=st.rerun)

    if st.session_state.get("inv_form"):
        project_opts = _get_project_options()
        with st.form("inv_form"):
            st.markdown("**新增发票记录**")
            ii1, ii2 = st.columns(2)
            invoice_code = ii1.text_input("发票编号 *")
            proj_ids = list(project_opts.keys())
            proj_id = ii2.selectbox("所属项目 *", proj_ids,
                                     format_func=lambda x: project_opts.get(x, str(x)))
            invoice_type = ii1.selectbox("发票类型", INVOICE_TYPES)
            invoice_direction = ii2.selectbox("方向", ["进项", "销项"])
            amount = ii1.number_input("金额（元）", min_value=0.0, step=1000.0)
            tax_rate = ii2.number_input("税率", min_value=0.0, max_value=1.0, value=0.09, step=0.01)
            invoice_date = ii1.date_input("开票日期", value=datetime.date.today())
            remarks = st.text_area("备注")
            ok = st.form_submit_button("保存", type="primary")
        if ok:
            if not invoice_code:
                st.error("发票编号为必填")
            else:
                r = api.post_create("/invoices", {
                    "invoice_code": invoice_code, "project_id": proj_id,
                    "invoice_type": invoice_type, "invoice_direction": invoice_direction,
                    "amount": amount, "tax_rate": tax_rate,
                    "invoice_date": invoice_date.isoformat(), "remarks": remarks,
                })
                if r and "_error" not in r:
                    st.success("发票记录已新增！")
                    st.session_state["inv_form"] = False
                    st.rerun()
                else:
                    st.error(r.get("_error", "失败") if r else "失败")

    if items:
        st.caption(f"共 {len(items)} 条发票记录")
        rows = [{
            "ID": i["id"],
            "发票编号": i.get("invoice_code", ""),
            "发票类型": i.get("invoice_type", ""),
            "方向": i.get("invoice_direction", ""),
            "金额": fmt_wan(i.get("amount")),
            "税率": f"{float(i.get('tax_rate') or 0)*100:.0f}%",
            "开票日期": fmt_date(i.get("invoice_date")),
            "认证状态": i.get("certification_status", ""),
            "审批状态": i.get("approval_status", ""),
        } for i in items]
        df = pd.DataFrame(rows)
        sel = st.dataframe(df.drop(columns=["ID"]), use_container_width=True, height=350,
                           on_select="rerun", selection_mode="single-row")
        if sel and sel.selection.rows:
            iid = df.iloc[sel.selection.rows[0]]["ID"]
            selected = next((i for i in items if i["id"] == iid), {})
            appr_st = selected.get("approval_status", "")
            if has_perm("workflow:create") and appr_st in ("待提交", "已驳回", ""):
                if st.button("🚀 提交发票审批", key="inv_appr"):
                    r = api.post(f"/invoices/{iid}/submit-approval")
                    st.success("已提交！") if r and "_error" not in r else st.error("失败")
                    st.rerun()
    else:
        st.info("暂无发票记录")
