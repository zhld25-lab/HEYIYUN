"""经营驾驶舱 — KPI + 图表"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import api_client as api
from utils import init_session, require_login, sidebar_nav, fmt_wan, fmt_pct

st.set_page_config(page_title="经营驾驶舱 · ERP", page_icon="📊", layout="wide")
init_session()
require_login()
sidebar_nav()


def render():
    st.markdown("## 📊 经营驾驶舱")

    with st.spinner("加载数据…"):
        summary = api.get("/dashboard/summary") or {}
        status_dist = api.get("/dashboard/project-status") or []
        finance = api.get("/dashboard/finance-summary") or {}
        cashflow = api.get("/dashboard/cashflow") or []
        cost_breakdown = api.get("/dashboard/cost-breakdown") or []
        profit_top = api.get("/dashboard/project-profit-top") or []

    # ── KPI 行 1 ──────────────────────────────────────────────────────────
    st.markdown("### 🏢 经营 KPI")
    cols = st.columns(7)
    metrics = [
        ("项目总数", summary.get("project_count", 0), None),
        ("在建项目", summary.get("active_project_count", 0), None),
        ("高风险", summary.get("high_risk_count", 0), None),
        ("合同总额", fmt_wan(summary.get("contract_amount")), None),
        ("累计回款", fmt_wan(summary.get("received_amount")), None),
        ("累计付款", fmt_wan(summary.get("paid_amount")), None),
        ("当前利润", fmt_wan(summary.get("current_profit")), None),
    ]
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label, value, delta)

    st.markdown("---")

    # ── KPI 行 2 (财务) ───────────────────────────────────────────────────
    st.markdown("### 💰 财务概览")
    f_cols = st.columns(4)
    f_metrics = [
        ("实际成本合计", fmt_wan(finance.get("total_actual_cost"))),
        ("应收款合计", fmt_wan(finance.get("total_receivable"))),
        ("应付款合计", fmt_wan(finance.get("total_payable"))),
        ("利润合计", fmt_wan(finance.get("total_profit"))),
    ]
    for col, (label, value) in zip(f_cols, f_metrics):
        col.metric(label, value)

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # ── 项目状态分布 ──────────────────────────────────────────────────────
    with col_l:
        st.markdown("#### 项目状态分布")
        if status_dist:
            df = pd.DataFrame(status_dist)
            fig = px.pie(df, values="count", names="status", hole=0.45,
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(height=300, margin=dict(t=10, b=10, l=0, r=0),
                               legend=dict(orientation="v", x=1.0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无项目状态数据")

    # ── 成本构成 ──────────────────────────────────────────────────────────
    with col_r:
        st.markdown("#### 成本构成")
        masked = cost_breakdown and cost_breakdown[0].get("amount") == "***"
        if cost_breakdown and not masked:
            df = pd.DataFrame(cost_breakdown)
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            fig = px.pie(df, values="amount", names="cost_type", hole=0.45,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(height=300, margin=dict(t=10, b=10, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("需要 **finance:view** 权限查看金额图表" if masked else "暂无成本数据")

    # ── 月度现金流 ────────────────────────────────────────────────────────
    st.markdown("#### 月度回款 / 付款趋势")
    masked_cf = cashflow and cashflow[0].get("received") == "***"
    if cashflow and not masked_cf:
        df_cf = pd.DataFrame(cashflow)
        for c in ["received", "paid", "net"]:
            df_cf[c] = pd.to_numeric(df_cf[c], errors="coerce") / 10000
        fig = go.Figure()
        fig.add_bar(x=df_cf["month"], y=df_cf["received"], name="回款（万）", marker_color="#52c41a")
        fig.add_bar(x=df_cf["month"], y=df_cf["paid"], name="付款（万）", marker_color="#ff7875")
        fig.add_scatter(x=df_cf["month"], y=df_cf["net"], name="净现金流（万）",
                        mode="lines+markers", line=dict(color="#1677ff", width=2))
        fig.update_layout(barmode="group", height=340,
                           margin=dict(t=10, b=10),
                           legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("需要 **finance:view** 权限查看现金流图表" if masked_cf else "暂无现金流数据")

    # ── 项目利润 Top 10 ───────────────────────────────────────────────────
    st.markdown("#### 项目利润 Top 10")
    masked_p = profit_top and profit_top[0].get("profit") == "***"
    if profit_top and not masked_p:
        df_p = pd.DataFrame(profit_top)
        df_p["profit_wan"] = pd.to_numeric(df_p["profit"], errors="coerce") / 10000
        df_p = df_p.sort_values("profit_wan", ascending=True)
        fig = px.bar(df_p, x="profit_wan", y="project_name", orientation="h",
                     color="profit_wan", color_continuous_scale=["#ff4d4f", "#faad14", "#52c41a"],
                     labels={"profit_wan": "利润（万元）", "project_name": "项目"})
        fig.update_layout(height=max(200, len(df_p) * 42), margin=dict(t=10, b=10),
                           coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("需要 **finance:view** 权限查看利润排行" if masked_p else "暂无利润数据")


render()
