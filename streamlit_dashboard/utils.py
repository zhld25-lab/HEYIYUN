"""Shared utilities: session management, sidebar, formatters."""
from __future__ import annotations

import streamlit as st

# ── Session ────────────────────────────────────────────────────────────────

def init_session():
    for key, default in [("token", ""), ("user", None)]:
        if key not in st.session_state:
            st.session_state[key] = default


def require_login():
    if not st.session_state.get("token"):
        st.warning("请先登录。")
        st.stop()


def get_user() -> dict:
    return st.session_state.get("user") or {}


def has_perm(code: str) -> bool:
    user = get_user()
    return code in (user.get("permission_codes") or [])


# ── Sidebar ────────────────────────────────────────────────────────────────

def sidebar_nav():
    user = get_user()
    with st.sidebar:
        st.markdown("## ⚡ 电力工程 ERP")
        st.markdown(f"👤 **{user.get('full_name', '')}**")
        st.caption(user.get("role_name", ""))
        st.markdown("---")
        st.page_link("app.py", label="📊 经营驾驶舱", icon="📊")
        st.page_link("pages/1_📊_驾驶舱.py", label="经营驾驶舱")
        st.page_link("pages/2_🏗️_项目中心.py", label="🏗️ 项目中心")
        st.page_link("pages/3_📄_合同中心.py", label="📄 合同中心")
        st.page_link("pages/4_💰_成本资金.py", label="💰 成本资金中心")
        st.page_link("pages/5_✅_审批中心.py", label="✅ 审批中心")
        st.page_link("pages/6_⚙️_系统设置.py", label="⚙️ 系统设置")
        st.markdown("---")
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.token = ""
            st.session_state.user = None
            st.rerun()


# ── Formatters ─────────────────────────────────────────────────────────────

def fmt_wan(v, unit: str = "万元") -> str:
    if v is None or v == "***":
        return "***"
    try:
        return f"¥ {float(v)/10000:,.1f} {unit}"
    except (TypeError, ValueError):
        return str(v)


def fmt_pct(v) -> str:
    if v is None or v == "***":
        return "***"
    try:
        return f"{float(v)*100:.1f}%"
    except (TypeError, ValueError):
        return str(v)


def fmt_date(v) -> str:
    if not v:
        return "-"
    return str(v)[:10]


APPROVAL_STATUS_COLOR = {
    "待提交": "gray", "审批中": "blue", "已批准": "green",
    "已驳回": "red", "已撤回": "orange",
}

WF_STATUS_LABEL = {
    "draft": "草稿", "pending": "审批中", "approved": "已批准",
    "rejected": "已驳回", "withdrawn": "已撤回",
}

WF_STATUS_ICON = {
    "draft": "📝", "pending": "🔵", "approved": "✅",
    "rejected": "❌", "withdrawn": "↩️",
}

STEP_STATUS_ICON = {
    "approved": "✅", "rejected": "❌", "pending": "🔵",
    "waiting": "⚪", "transferred": "🔀",
}
