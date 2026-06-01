from __future__ import annotations

import plotly.express as px
import streamlit as st

from components.data_table import render_export_button, render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.document_service import get_document_completion_by_project, get_missing_documents
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("资料档案中心")
init_session_state()
role = render_sidebar()
render_page_header("资料档案中心", "管理项目立项、报装、合同、设计、施工、安全、质量、试验、竣工、结算和归档资料。")

documents = get_dataset("documents")
c1, c2, c3 = st.columns(3)
project = c1.selectbox("所属项目", ["全部"] + sorted(documents["project_name"].unique()))
doc_type = c2.selectbox("资料类型", ["全部"] + sorted(documents["document_type"].unique()))
missing = c3.selectbox("是否缺失", ["全部", "是", "否"])
filtered = documents.copy()
if project != "全部":
    filtered = filtered[filtered["project_name"] == project]
if doc_type != "全部":
    filtered = filtered[filtered["document_type"] == doc_type]
if missing != "全部":
    filtered = filtered[filtered["is_missing"] == (missing == "是")]

completion = get_document_completion_by_project()
fig = px.bar(completion, x="completion_rate", y="project_name", orientation="h", title="资料完整率排名", template="plotly_white", labels={"completion_rate": "完整率", "project_name": "项目"})
fig.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

tabs = st.tabs(["资料列表", "缺失资料提醒", "按项目查看", "模拟上传附件", "资料审核流程"])
with tabs[0]:
    render_export_button(to_display_df(filtered), "document_list_export.xlsx")
    render_filterable_table(to_display_df(filtered), height=360)
with tabs[1]:
    render_filterable_table(to_display_df(get_missing_documents()), height=340)
with tabs[2]:
    render_filterable_table(to_display_df(filtered.sort_values(["project_name", "document_type"])), height=340)
with tabs[3]:
    uploaded = st.file_uploader("模拟上传项目资料", type=["pdf", "docx", "xlsx", "png", "jpg"])
    if uploaded:
        st.success(f"已模拟接收附件：{uploaded.name}")
with tabs[4]:
    st.info("资料员上传 → 项目经理审核 → 资料负责人复核 → 归档。缺失资料会进入风险预警中心。")
    render_filterable_table(to_display_df(filtered[["document_no", "document_name", "project_name", "audit_status", "is_required", "is_missing", "version"]]), height=300)

render_business_note("资料档案中心通过必传项和缺失状态计算资料完整率，低于 80% 会触发资料风险，低于 60% 触发高风险。")

