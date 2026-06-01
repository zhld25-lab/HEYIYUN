"""系统设置 — 用户列表、操作日志"""
from __future__ import annotations

import streamlit as st
import pandas as pd

import api_client as api
from utils import init_session, require_login, sidebar_nav, has_perm, fmt_date

st.set_page_config(page_title="系统设置 · ERP", page_icon="⚙️", layout="wide")
init_session()
require_login()
sidebar_nav()

st.markdown("## ⚙️ 系统设置")

tab_users, tab_audit = st.tabs(["👥 用户管理", "📋 操作日志"])

with tab_users:
    if not has_perm("user:view"):
        st.warning("您没有查看用户列表的权限（需要 user:view）")
    else:
        with st.spinner("加载用户列表…"):
            users = api.get("/users") or []
        if users:
            rows = [{
                "用户名": u.get("username", ""),
                "姓名": u.get("full_name", ""),
                "角色": u.get("role_name", ""),
                "状态": "启用" if u.get("is_active", True) else "禁用",
            } for u in users]
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("暂无用户数据")

with tab_audit:
    if not has_perm("audit:view"):
        st.warning("您没有查看操作日志的权限（需要 audit:view）")
    else:
        with st.expander("🔍 过滤", expanded=False):
            c1, c2 = st.columns(2)
            f_resource = c1.selectbox("资源类型", ["全部", "project", "contract", "cost", "payment", "receipt", "invoice", "workflow"])
            f_action = c2.selectbox("操作类型", ["全部", "CREATE", "UPDATE", "DELETE"])

        params: dict = {"page_size": 100}
        if f_resource != "全部":
            params["resource_type"] = f_resource
        if f_action != "全部":
            params["action"] = f_action

        with st.spinner("加载操作日志…"):
            data = api.get("/system/audit-logs", params=params) or {}
        logs = data.get("items", []) if isinstance(data, dict) else []

        if logs:
            st.caption(f"共 {data.get('total', len(logs))} 条日志")
            rows = [{
                "时间": l.get("created_at", "")[:16],
                "操作人": l.get("username", ""),
                "操作": l.get("action", ""),
                "资源类型": l.get("resource_type", ""),
                "资源 ID": l.get("resource_id", ""),
                "IP": l.get("ip_address", ""),
            } for l in logs]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=500)
        else:
            st.info("暂无操作日志")

# ── 当前账号信息 ───────────────────────────────────────────────────────────
st.markdown("---")
user = st.session_state.get("user") or {}
with st.expander("👤 当前账号信息"):
    st.write(f"**用户名：** {user.get('username')}")
    st.write(f"**姓名：** {user.get('full_name')}")
    st.write(f"**角色：** {user.get('role_name')}")
    perms = user.get("permission_codes", [])
    st.write(f"**权限（{len(perms)} 项）：**")
    st.code(" · ".join(perms))
