import streamlit as st

from config.role_config import ROLE_USERS, ROLES
from config.settings import DEFAULT_ROLE


def init_session_state() -> None:
    if "current_role" not in st.session_state:
        st.session_state.current_role = DEFAULT_ROLE if DEFAULT_ROLE in ROLES else ROLES[0]
    if "current_user" not in st.session_state:
        st.session_state.current_user = ROLE_USERS.get(st.session_state.current_role, "演示用户")


def set_current_role(role: str) -> None:
    st.session_state.current_role = role
    st.session_state.current_user = ROLE_USERS.get(role, "演示用户")

