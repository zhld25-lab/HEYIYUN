from __future__ import annotations

import plotly.express as px
import streamlit as st

from components.data_table import render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("安全质量中心")
init_session_state()
role = render_sidebar()
render_page_header("安全质量中心", "体现工程企业安全质量闭环：发现问题、下发整改、上传资料、复查、关闭或升级。")

records = get_dataset("safety_quality")
c1, c2, c3 = st.columns(3)
category = c1.selectbox("类别", ["全部", "安全", "质量"])
closed = c2.selectbox("是否闭环", ["全部", "是", "否"])
project = c3.selectbox("所属项目", ["全部"] + sorted(records["project_name"].unique()))
filtered = records.copy()
if category != "全部":
    filtered = filtered[filtered["category"] == category]
if closed != "全部":
    filtered = filtered[filtered["is_closed"] == (closed == "是")]
if project != "全部":
    filtered = filtered[filtered["project_name"] == project]

cols = st.columns(4)
cols[0].metric("安全质量记录", len(filtered))
cols[1].metric("未闭环", int((~filtered["is_closed"]).sum()) if not filtered.empty else 0)
cols[2].metric("安全隐患", int((filtered["category"] == "安全").sum()) if not filtered.empty else 0)
cols[3].metric("质量问题", int((filtered["category"] == "质量").sum()) if not filtered.empty else 0)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["安全检查", "安全隐患", "整改复查", "安全教育", "质量检查", "缺陷整改"])
with tab1:
    render_filterable_table(to_display_df(filtered[filtered["category"] == "安全"]), height=340)
with tab2:
    render_filterable_table(to_display_df(filtered[(filtered["category"] == "安全") & (~filtered["is_closed"])]), height=340)
with tab3:
    render_filterable_table(to_display_df(filtered[["record_no", "project_name", "issue_type", "rectify_deadline", "rectify_status", "review_result", "is_closed"]]), height=340)
with tab4:
    st.info("安全教育记录与班前会、特种作业人员、高风险作业联动。Demo 使用安全质量记录模拟。")
    render_filterable_table(to_display_df(filtered[filtered["category"] == "安全"].head(12)), height=300)
with tab5:
    render_filterable_table(to_display_df(filtered[filtered["category"] == "质量"]), height=340)
with tab6:
    render_filterable_table(to_display_df(filtered[(filtered["category"] == "质量") & (~filtered["is_closed"])]), height=340)

if not filtered.empty:
    chart_df = filtered.groupby(["category", "rectify_status"], as_index=False)["id"].count()
    fig = px.bar(chart_df, x="rectify_status", y="id", color="category", title="安全质量整改状态分布", template="plotly_white", labels={"id": "记录数", "rectify_status": "整改状态", "category": "类别"})
    st.plotly_chart(fig, use_container_width=True)

render_business_note("安全质量中心重点呈现闭环状态，未关闭的问题会同步进入项目健康度和风险预警计算。")

