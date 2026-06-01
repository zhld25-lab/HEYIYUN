from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, STYLE_FILE


def setup_page(title: str = APP_NAME) -> None:
    st.set_page_config(page_title=title, page_icon="⚡", layout="wide")
    load_global_css()


def load_global_css() -> None:
    if STYLE_FILE.exists():
        st.markdown(f"<style>{STYLE_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"<div class='erp-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='erp-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def render_business_note(text: str) -> None:
    st.markdown(f"<div class='section-note'>{text}</div>", unsafe_allow_html=True)

