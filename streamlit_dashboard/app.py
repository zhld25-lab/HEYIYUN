"""电力工程 ERP · Streamlit 全站入口

多页面应用：登录后自动跳转到经营驾驶舱。
其余页面位于 pages/ 目录。

运行：
  cd streamlit_dashboard
  pip install -r requirements.txt
  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="电力工程 ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

import api_client as api
from utils import init_session, require_login, sidebar_nav

init_session()

if not st.session_state.token:
    # ── 登录页 ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style='text-align:center;padding:60px 0 20px'>
          <h1 style='color:#1677ff'>⚡ 电力工程企业项目经营管理平台</h1>
          <p style='color:#666'>Power Engineering ERP & Project Management</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="admin / manager / finance ...")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("🔐 登 录", use_container_width=True, type="primary")

        if submitted:
            with st.spinner("验证身份…"):
                data = api.login(username, password)
            if data:
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.success("登录成功，正在跳转…")
                st.rerun()
            else:
                st.error("用户名或密码错误，或后端服务未启动。")

        st.caption("测试账号：admin/Admin123456 · manager/Manager123456 · finance/Finance123456 · pm/PM123456")
else:
    # ── 已登录：显示驾驶舱内容（home page） ────────────────────────────
    import importlib
    dashboard = importlib.import_module("pages.1_📊_驾驶舱")
    dashboard.render()
