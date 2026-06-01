from __future__ import annotations

import streamlit as st

from config.settings import ASSETS_DIR
from config.role_config import ROLE_USERS, ROLES
from services.permission_service import get_visible_modules_by_role
from utils.session_state import set_current_role


def render_sidebar() -> str:
    logo = ASSETS_DIR / "logo.png"
    if logo.exists():
        st.sidebar.image(str(logo), width=48)
    st.sidebar.markdown("## ⚡ HEYIYUN ERP")
    st.sidebar.caption("项目全生命周期经营管理系统 Demo")
    current_role = st.session_state.get("current_role", "总经理")
    role = st.sidebar.selectbox("当前登录角色", ROLES, index=ROLES.index(current_role) if current_role in ROLES else 0)
    if role != current_role:
        set_current_role(role)
    st.sidebar.text_input("当前登录用户", value=ROLE_USERS.get(role, "演示用户"), disabled=True)
    modules = get_visible_modules_by_role(role)
    if modules == ["全部模块"]:
        st.sidebar.success("当前角色可查看全部模块")
    else:
        st.sidebar.info("可见模块：" + "、".join(modules[:6]) + ("..." if len(modules) > 6 else ""))
    if st.sidebar.button("刷新演示数据", use_container_width=True):
        st.cache_data.clear()
        st.success("已刷新演示数据")
    st.sidebar.download_button(
        "导出演示说明",
        data="HEYIYUN 中国电力工程企业项目经营管理平台 Demo\n数据均为模拟数据。",
        file_name="demo_readme.txt",
        mime="text/plain",
        use_container_width=True,
    )
    st.sidebar.caption("页面导航请使用左侧 Streamlit 多页面菜单。")
    return role
