from __future__ import annotations

import streamlit as st

from components.data_table import render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.equipment_service import detect_equipment_risks
from services.permission_service import mask_sensitive_fields
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("设备周材中心")
init_session_state()
role = render_sidebar()
render_page_header("设备周材中心", "管理吊车、挖机、电缆牵引机、试验设备、安全工器具、脚手架、模板、围挡等设备周材。")

equipment = get_dataset("equipment")
c1, c2 = st.columns(2)
status = c1.selectbox("当前状态", ["全部"] + sorted(equipment["current_status"].unique()))
project = c2.selectbox("当前项目", ["全部"] + sorted(equipment["project_name"].unique()))
filtered = equipment.copy()
if status != "全部":
    filtered = filtered[filtered["current_status"] == status]
if project != "全部":
    filtered = filtered[filtered["project_name"] == project]

labels = ["设备台账", "设备调度", "设备使用记录", "设备维修", "设备保养", "设备租赁", "周材租赁", "租赁结算"]
tabs = st.tabs(labels)
for label, tab in zip(labels, tabs):
    with tab:
        render_filterable_table(to_display_df(mask_sensitive_fields(filtered, role)), label, height=360)

st.subheader("设备周材风险")
render_filterable_table(to_display_df(mask_sensitive_fields(detect_equipment_risks(filtered), role)), height=260)
render_business_note("设备周材中心用于监控设备闲置、超期未保养、租赁费用超预算、未归还和使用记录缺失等风险。")
