from __future__ import annotations

import streamlit as st

from utils.formatters import format_money, format_percent


def render_project_card(project: dict) -> None:
    st.markdown(
        f"""
        <div class="project-card">
          <strong>{project.get('project_name')}</strong>
          <div class="small-muted">{project.get('project_no')} · {project.get('project_type')} · {project.get('voltage_level')}</div>
          <div>项目经理：{project.get('project_manager')}　状态：{project.get('status')}　风险：{project.get('risk_level')}</div>
          <div>合同金额：{format_money(project.get('contract_amount'))}　产值进度：{format_percent(project.get('output_progress'))}　收款进度：{format_percent(project.get('collection_progress'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

