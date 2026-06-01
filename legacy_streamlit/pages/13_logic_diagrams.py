from __future__ import annotations

import streamlit as st

from components.layout import render_business_note, render_page_header, setup_page
from components.mermaid_view import render_business_flow_explanation, render_mermaid_code
from components.sidebar import render_sidebar
from utils.session_state import init_session_state


setup_page("逻辑图中心")
init_session_state()
role = render_sidebar()
render_page_header("逻辑图中心", "展示项目全生命周期、数据关联、合同成本资金、采购、安全质量、审批和风险联动逻辑。")

diagrams = [
    (
        "项目全生命周期图",
        "graph LR\nA[立项]-->B[报装]-->C[合同]-->D[采购]-->E[施工]-->F[安全质量]-->G[工程量确认]-->H[成本归集]-->I[付款回款]-->J[发票]-->K[结算]-->L[竣工资料]-->M[复盘]",
        "对应项目中心、施工现场中心、成本资金中心、资料档案中心和项目复盘逻辑。",
    ),
    (
        "项目数据关联图",
        "graph TD\nP[项目]-->C[合同]\nP-->CO[成本]\nP-->F[资金]\nP-->M[材料]\nP-->E[设备]\nP-->S[施工]\nP-->SA[安全]\nP-->Q[质量]\nP-->D[资料]\nP-->W[审批]\nP-->R[风险]",
        "系统所有业务数据均通过 project_id 回到项目主数据，便于项目维度经营分析。",
    ),
    (
        "合同-成本-资金图",
        "graph TD\nA[承包合同]-->B[回款]-->C[销项发票]-->D[项目收入]\nE[分包合同]-->F[付款]-->G[进项发票]-->H[项目成本]\nI[采购合同]-->J[材料入库]-->K[成本归集]-->F\nL[租赁合同]-->M[使用记录]-->N[租赁结算]-->F",
        "对应合同中心和成本资金中心，体现收入、支出、发票和结算的联动。",
    ),
    (
        "采购物资流程图",
        "graph LR\nA[材料计划]-->B[采购申请]-->C[采购合同]-->D[到货验收]-->E[入库]-->F[领用出库]-->G[项目成本]",
        "对应采购物资中心，材料从计划到领用后归集为项目成本。",
    ),
    (
        "安全隐患闭环图",
        "graph LR\nA[检查]-->B[发现隐患]-->C[整改通知]-->D[责任人整改]-->E[复查]-->F[闭环]\nE-->G[升级]",
        "对应安全质量中心，未闭环隐患会进入风险预警。",
    ),
    (
        "质量问题闭环图",
        "graph LR\nA[质量检查]-->B[缺陷记录]-->C[整改]-->D[复验]-->E[验收]-->F[归档]",
        "对应质量检查、缺陷整改、隐蔽工程验收和竣工资料。",
    ),
    (
        "审批流图",
        "graph LR\nA[发起]-->B[部门负责人]-->C[项目经理]-->D[财务负责人]-->E[总经理]-->F[完成]\nE-->G[驳回]",
        "对应审批中心，审批超时会触发审批风险。",
    ),
    (
        "风险预警联动图",
        "graph TD\nP[项目]-->A[进度风险]\nP-->B[成本风险]\nP-->C[资金风险]\nP-->D[安全风险]\nP-->E[质量风险]\nP-->F[资料风险]\nP-->G[审批风险]",
        "对应风险预警中心，风险评分汇总多个业务模块的异常指标。",
    ),
]

for title, code, explanation in diagrams:
    render_mermaid_code(title, code)
    render_business_flow_explanation(explanation)

render_business_note("逻辑图中心以 Mermaid 文本展示业务关系，可直接复制到支持 Mermaid 的文档或 GitHub Markdown 中渲染。")

