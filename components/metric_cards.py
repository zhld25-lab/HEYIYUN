from __future__ import annotations

import streamlit as st


def render_metric_card(label: str, value: str, delta: str = "", accent: str = "#0891b2") -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="border-left-color:{accent}">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_grid(metrics: list[dict], columns: int = 4) -> None:
    cols = st.columns(columns)
    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            render_metric_card(
                metric.get("label", ""),
                metric.get("value", "-"),
                metric.get("delta", ""),
                metric.get("accent", "#0891b2"),
            )

