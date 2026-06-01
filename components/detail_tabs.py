from __future__ import annotations

import streamlit as st

from components.charts import render_cost_breakdown_chart, render_progress_bar
from components.data_table import render_filterable_table
from components.risk_badge import render_risk_summary
from services.cost_service import calculate_cost_breakdown, calculate_cost_variance, detect_cost_overrun
from services.project_service import calculate_project_health_score
from services.risk_service import calculate_project_risk
from utils.formatters import format_money, format_percent, to_display_df


def render_project_detail_tabs(project: dict, related: dict) -> None:
    tabs = st.tabs(["基本信息", "进度节点", "合同", "成本", "资金", "采购物资", "设备周材", "安全质量", "资料档案", "风险预警", "审批记录"])
    with tabs[0]:
        col1, col2, col3 = st.columns(3)
        col1.write(f"**项目编号：** {project.get('project_no')}")
        col1.write(f"**项目名称：** {project.get('project_name')}")
        col1.write(f"**项目类型：** {project.get('project_type')}")
        col1.write(f"**电压等级：** {project.get('voltage_level')}")
        col2.write(f"**项目地址：** {project.get('address')}")
        col2.write(f"**建设单位：** {project.get('owner')}")
        col2.write(f"**施工单位：** {project.get('constructor')}")
        col2.write(f"**设计单位：** {project.get('designer')}")
        col3.write(f"**监理单位：** {project.get('supervisor')}")
        col3.write(f"**项目经理：** {project.get('project_manager')}")
        col3.write(f"**项目状态：** {project.get('status')}")
        col3.write(f"**计划周期：** {project.get('planned_start'):%Y-%m-%d} 至 {project.get('planned_end'):%Y-%m-%d}")
        st.info(project.get("description", ""))
        health = calculate_project_health_score(project, related)
        st.subheader("项目健康度评分")
        render_risk_summary({"risk_score": health["health_score"], "risk_level": health["health_level"], "risk_reasons": health["risk_reasons"], "recommended_actions": health["recommended_actions"]})

    with tabs[1]:
        render_filterable_table(to_display_df(related.get("progress")), "关键进度节点")

    with tabs[2]:
        render_filterable_table(to_display_df(related.get("contracts")), "项目关联合同")

    with tabs[3]:
        variance = calculate_cost_variance(project)
        overrun = detect_cost_overrun(project)
        cols = st.columns(4)
        cols[0].metric("目标成本", format_money(variance["target_cost"]))
        cols[1].metric("实际成本", format_money(variance["actual_cost"]))
        cols[2].metric("成本偏差", format_money(variance["variance"]))
        cols[3].metric("成本风险", overrun["level"])
        render_cost_breakdown_chart(calculate_cost_breakdown(related.get("costs")))
        render_filterable_table(to_display_df(related.get("costs")), "成本明细")

    with tabs[4]:
        cols = st.columns(4)
        cols[0].metric("合同金额", format_money(project.get("contract_amount")))
        cols[1].metric("已收款", format_money(project.get("received_amount")))
        cols[2].metric("已付款", format_money(project.get("paid_amount")))
        cols[3].metric("预计利润", format_money(project.get("expected_profit")))
        render_progress_bar("产值进度", project.get("output_progress", 0))
        render_progress_bar("收款进度", project.get("collection_progress", 0))
        render_filterable_table(to_display_df(related.get("finance")), "资金流水")

    with tabs[5]:
        render_filterable_table(to_display_df(related.get("materials")), "采购物资")

    with tabs[6]:
        render_filterable_table(to_display_df(related.get("equipment")), "设备周材")

    with tabs[7]:
        render_filterable_table(to_display_df(related.get("safety_quality")), "安全质量记录")

    with tabs[8]:
        render_progress_bar("资料完整率", project.get("document_completion", 0))
        render_filterable_table(to_display_df(related.get("documents")), "资料档案")

    with tabs[9]:
        risk_result = calculate_project_risk(project, related)
        render_risk_summary(risk_result)
        render_filterable_table(to_display_df(related.get("risks")), "风险预警")

    with tabs[10]:
        render_filterable_table(to_display_df(related.get("workflows")), "审批记录")


def render_contract_detail_tabs(contract: dict, related: dict | None = None) -> None:
    tabs = st.tabs(["基本信息", "所属项目", "收付款计划", "发票记录", "变更签证", "结算记录", "附件资料", "审批流程", "操作日志"])
    with tabs[0]:
        col1, col2, col3 = st.columns(3)
        col1.write(f"**合同编号：** {contract.get('contract_no')}")
        col1.write(f"**合同名称：** {contract.get('contract_name')}")
        col1.write(f"**合同类型：** {contract.get('contract_type')}")
        col2.write(f"**甲方：** {contract.get('party_a')}")
        col2.write(f"**乙方：** {contract.get('party_b')}")
        col2.write(f"**合同状态：** {contract.get('contract_status')}")
        col3.write(f"**合同金额：** {format_money(contract.get('contract_amount'))}")
        col3.write(f"**结算金额：** {format_money(contract.get('settlement_amount'))}")
        col3.write(f"**归档状态：** {contract.get('archive_status')}")
    with tabs[1]:
        st.info(f"所属项目：{contract.get('project_name')}，project_id={contract.get('project_id')}")
    with tabs[2]:
        st.write(f"已收款：{format_money(contract.get('received_amount'))}；已付款：{format_money(contract.get('paid_amount'))}；应收：{format_money(contract.get('receivable'))}；应付：{format_money(contract.get('payable'))}")
    with tabs[3]:
        st.write(f"累计发票金额：{format_money(contract.get('invoice_amount'))}")
    with tabs[4]:
        st.info("Demo 中签证变更与合同结算关联展示，真实系统可拆分为独立变更台账。")
    with tabs[5]:
        st.write(f"当前结算金额：{format_money(contract.get('settlement_amount'))}")
    with tabs[6]:
        st.info("合同正文、补充协议、审批单、结算书等附件在资料档案中心统一归档。")
    with tabs[7]:
        st.write(f"审批状态：{contract.get('approval_status')}")
    with tabs[8]:
        st.caption("创建合同 > 提交审批 > 合同执行 > 发票/收付款 > 结算 > 归档")

