"""HTTP client for the FastAPI backend."""
from __future__ import annotations

import os
import requests
import streamlit as st

BASE_URL = (
    st.secrets.get("ERP_API_URL")
    or os.getenv("ERP_API_URL", "http://localhost:8000/api/v1")
)
TIMEOUT = 15


def _headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def login(username: str, password: str) -> dict | None:
    """Login and return {access_token, user} or None."""
    try:
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("data")
    except requests.RequestException:
        pass
    return None


def get(path: str, params: dict | None = None):
    """GET request. Returns data field or None on error."""
    try:
        r = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json().get("data")
        if r.status_code == 401:
            st.session_state.token = ""
            st.warning("登录已过期，请重新登录")
            st.rerun()
    except requests.RequestException as e:
        st.toast(f"网络错误：{e}", icon="⚠️")
    return None


def post(path: str, json: dict | None = None) -> dict | None:
    """POST request for actions (approve/reject/etc). Returns data or error dict."""
    try:
        r = requests.post(f"{BASE_URL}{path}", headers=_headers(), json=json or {}, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json().get("data")
        return {"_error": r.json().get("detail", r.text), "_status": r.status_code}
    except requests.RequestException as e:
        return {"_error": str(e)}


def post_create(path: str, json: dict) -> dict | None:
    """POST to create a resource. Returns the created object data or error dict."""
    try:
        r = requests.post(f"{BASE_URL}{path}", headers=_headers(), json=json, timeout=TIMEOUT)
        if r.status_code in (200, 201):
            return r.json().get("data")
        return {"_error": r.json().get("detail", r.text), "_status": r.status_code}
    except requests.RequestException as e:
        return {"_error": str(e)}


def put(path: str, json: dict) -> dict | None:
    """PUT to update a resource."""
    try:
        r = requests.put(f"{BASE_URL}{path}", headers=_headers(), json=json, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json().get("data")
        return {"_error": r.json().get("detail", r.text), "_status": r.status_code}
    except requests.RequestException as e:
        return {"_error": str(e)}


def delete(path: str) -> bool | None:
    """DELETE request. Returns True on success."""
    try:
        r = requests.delete(f"{BASE_URL}{path}", headers=_headers(), timeout=TIMEOUT)
        return r.status_code in (200, 204)
    except requests.RequestException:
        return None
