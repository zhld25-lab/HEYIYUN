from __future__ import annotations

import streamlit as st
import pandas as pd

from utils.export_utils import dataframe_to_excel_bytes


def render_filterable_table(df: pd.DataFrame, title: str = "", height: int = 360, use_container_width: bool = True) -> None:
    if title:
        st.subheader(title)
    if df is None or df.empty:
        st.info("暂无符合条件的数据。")
        return
    st.dataframe(df, height=height, use_container_width=use_container_width, hide_index=True)


def render_status_table(df: pd.DataFrame, status_column: str = "状态", title: str = "") -> None:
    render_filterable_table(df, title=title)


def render_export_button(df: pd.DataFrame, file_name: str, label: str = "导出 Excel") -> None:
    if df is None or df.empty:
        st.button(label, disabled=True)
        return
    st.download_button(
        label=label,
        data=dataframe_to_excel_bytes(df),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

