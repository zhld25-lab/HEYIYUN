from __future__ import annotations

import streamlit as st


def get_risk_color(level: str) -> str:
    return {
        "低": "green",
        "中": "orange",
        "高": "red",
        "严重": "darkred",
        "优秀": "green",
        "正常": "blue",
        "关注": "orange",
        "风险": "red",
    }.get(level, "gray")


def render_risk_badge(level: str, label: str | None = None) -> None:
    color = get_risk_color(level)
    st.markdown(f"<span class='badge badge-{color}'>{label or level}</span>", unsafe_allow_html=True)


def render_risk_summary(risk_result: dict) -> None:
    render_risk_badge(risk_result.get("risk_level") or risk_result.get("health_level", "-"))
    st.metric("风险评分", risk_result.get("risk_score", risk_result.get("health_score", "-")))
    st.write("触发原因：")
    for reason in risk_result.get("risk_reasons", []):
        st.write(f"- {reason}")
    st.write("建议动作：")
    for action in risk_result.get("recommended_actions", []):
        st.write(f"- {action}")

