from __future__ import annotations

import streamlit as st


def render_mermaid_code(title: str, code: str) -> None:
    st.subheader(title)
    st.code(code, language="mermaid")


def render_business_flow_explanation(text: str) -> None:
    st.markdown(f"<div class='section-note'>{text}</div>", unsafe_allow_html=True)

