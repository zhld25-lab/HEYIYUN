from __future__ import annotations

import streamlit as st

from components.charts import render_bar_ranking
from components.data_table import render_export_button, render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from services.material_service import get_material_risks, get_supplier_ranking
from services.permission_service import mask_sensitive_fields
from utils.formatters import to_display_df
from utils.session_state import init_session_state


setup_page("采购物资中心")
init_session_state()
role = render_sidebar()
render_page_header("采购物资中心", "覆盖材料计划、采购申请、采购合同、到货验收、入库、领用、退货、盘点和成本归集。")

materials = get_dataset("materials")
c1, c2, c3 = st.columns(3)
category = c1.selectbox("材料分类", ["全部"] + sorted(materials["category"].unique()))
project = c2.selectbox("所属项目", ["全部"] + sorted(materials["project_name"].unique()))
risk_only = c3.checkbox("仅看采购风险")
filtered = materials.copy()
if category != "全部":
    filtered = filtered[filtered["category"] == category]
if project != "全部":
    filtered = filtered[filtered["project_name"] == project]
if risk_only:
    filtered = get_material_risks(filtered)

render_export_button(to_display_df(mask_sensitive_fields(filtered, role)), "material_list_export.xlsx")
labels = ["材料计划", "采购申请", "采购合同", "到货验收", "入库管理", "出库领用", "退货管理", "库存盘点", "供应商管理", "材料价格库"]
tabs = st.tabs(labels)
for idx, (label, tab) in enumerate(zip(labels, tabs)):
    with tab:
        if idx == 8:
            ranking = get_supplier_ranking().rename(columns={"supplier": "供应商", "total_amount": "采购金额"})
            render_bar_ranking(ranking, "采购金额", "供应商", "供应商采购金额排名")
        elif idx == 9:
            price = filtered[["material_code", "material_name", "specification", "unit", "budget_unit_price", "purchase_unit_price", "is_over_price"]]
            render_filterable_table(to_display_df(mask_sensitive_fields(price, role)), "材料价格库")
        else:
            render_filterable_table(to_display_df(mask_sensitive_fields(filtered, role)), label, height=360)

st.subheader("采购风险")
render_filterable_table(to_display_df(mask_sensitive_fields(get_material_risks(filtered), role)), height=260)
render_business_note("采购物资中心体现从材料计划到入库领用再到项目成本归集的闭环，重点识别采购超价、缺货、到货异常和未关联项目。")
