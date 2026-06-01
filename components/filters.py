from __future__ import annotations

import streamlit as st
import pandas as pd


def select_filter(label: str, values, key: str | None = None) -> str:
    options = ["全部"] + sorted([str(v) for v in pd.Series(values).dropna().unique()])
    return st.selectbox(label, options, key=key)


def keyword_filter(label: str = "关键词", key: str | None = None) -> str:
    return st.text_input(label, key=key, placeholder="输入项目名称、编号或关键字")

