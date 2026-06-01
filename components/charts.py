from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


PLOTLY_TEMPLATE = "plotly_white"


def render_cashflow_chart(cashflow: pd.DataFrame, title: str = "月度现金流") -> None:
    if cashflow.empty:
        st.info("暂无现金流数据。")
        return
    fig = go.Figure()
    fig.add_bar(x=cashflow["month"], y=cashflow["收入"], name="收入", marker_color="#0891b2")
    fig.add_bar(x=cashflow["month"], y=cashflow["支出"], name="支出", marker_color="#f97316")
    fig.add_scatter(x=cashflow["month"], y=cashflow["净现金流"], name="净现金流", mode="lines+markers", line=dict(color="#16a34a", width=3))
    fig.update_layout(title=title, template=PLOTLY_TEMPLATE, height=360, barmode="group", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)


def render_project_status_pie(projects: pd.DataFrame, title: str = "项目状态分布") -> None:
    if projects.empty:
        st.info("暂无项目数据。")
        return
    grouped = projects.groupby("status", as_index=False)["id"].count().rename(columns={"id": "项目数", "status": "项目状态"})
    fig = px.pie(grouped, names="项目状态", values="项目数", hole=0.42, title=title, template=PLOTLY_TEMPLATE)
    fig.update_layout(height=340, legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)


def render_cost_breakdown_chart(cost_breakdown: pd.DataFrame, title: str = "成本构成") -> None:
    if cost_breakdown.empty:
        st.info("暂无成本数据。")
        return
    fig = px.pie(cost_breakdown, names="cost_type", values="amount", hole=0.5, title=title, template=PLOTLY_TEMPLATE)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=360, legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)


def render_profit_ranking_chart(projects: pd.DataFrame, title: str = "项目利润排名 Top 10") -> None:
    if projects.empty:
        st.info("暂无项目利润数据。")
        return
    df = projects.sort_values("expected_profit", ascending=False).head(10)
    fig = px.bar(df, x="expected_profit", y="project_name", orientation="h", title=title, template=PLOTLY_TEMPLATE, color="profit_rate", color_continuous_scale="Teal")
    fig.update_layout(height=420, yaxis={"categoryorder": "total ascending"}, coloraxis_colorbar_title="利润率")
    st.plotly_chart(fig, use_container_width=True)


def render_risk_distribution_chart(risks: pd.DataFrame, title: str = "风险类型分布") -> None:
    if risks.empty:
        st.info("暂无风险数据。")
        return
    grouped = risks.groupby("risk_type", as_index=False)["id"].count().rename(columns={"id": "风险数", "risk_type": "风险类型"})
    fig = px.bar(grouped, x="风险类型", y="风险数", title=title, template=PLOTLY_TEMPLATE, color="风险数", color_continuous_scale="OrRd")
    fig.update_layout(height=360, xaxis_tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)


def render_progress_bar(label: str, value: float) -> None:
    st.caption(f"{label}：{value:.1%}")
    st.progress(max(0, min(1, float(value))))


def render_progress_scatter(projects: pd.DataFrame, title: str = "产值进度 vs 收款进度") -> None:
    fig = px.scatter(
        projects,
        x="output_progress",
        y="collection_progress",
        color="risk_level",
        size="contract_amount",
        hover_name="project_name",
        title=title,
        template=PLOTLY_TEMPLATE,
        labels={"output_progress": "产值进度", "collection_progress": "收款进度", "risk_level": "风险等级"},
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)


def render_bar_ranking(df: pd.DataFrame, x: str, y: str, title: str, color: str = "#0891b2") -> None:
    if df.empty:
        st.info("暂无排名数据。")
        return
    fig = px.bar(df, x=x, y=y, orientation="h", title=title, template=PLOTLY_TEMPLATE)
    fig.update_traces(marker_color=color)
    fig.update_layout(height=360, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

