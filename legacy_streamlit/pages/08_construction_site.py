from __future__ import annotations

import pandas as pd
import streamlit as st

from components.data_table import render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from data.data_loader import get_dataset
from utils.formatters import format_money, to_display_df
from utils.session_state import init_session_state


def build_site_tables(projects: pd.DataFrame, progress: pd.DataFrame) -> dict[str, pd.DataFrame]:
    active = projects[projects["status"].isin(["施工中", "验收中", "结算中"])]
    logs = []
    teams = []
    quantities = []
    changes = []
    for idx, project in active.reset_index(drop=True).iterrows():
        logs.append(
            {
                "日期": pd.Timestamp("2026-05-01") + pd.Timedelta(days=idx),
                "所属项目": project["project_name"],
                "天气": ["晴", "多云", "小雨"][idx % 3],
                "施工内容": "电缆敷设、设备基础复核、配电柜安装",
                "施工部位": ["配电房", "电缆沟", "箱变基础"][idx % 3],
                "班组": f"电气安装{idx % 4 + 1}班",
                "人数": 8 + idx % 9,
                "机械设备": "电缆牵引机、发电机、吊车",
                "完成工程量": f"{30 + idx * 4} 米 / {idx % 3 + 1} 台",
                "存在问题": "材料到货需跟进" if idx % 4 == 0 else "无重大问题",
                "记录人": project["project_manager"],
            }
        )
        teams.append(
            {
                "班组名称": f"电气安装{idx % 4 + 1}班",
                "班组长": f"班组长{idx + 1}",
                "工种": ["电缆工", "一次安装", "二次接线", "土建配合"][idx % 4],
                "人数": 8 + idx % 9,
                "所属项目": project["project_name"],
                "进场时间": project["planned_start"] + pd.Timedelta(days=45),
                "退场时间": project["planned_end"] - pd.Timedelta(days=10),
                "安全教育状态": "已教育" if idx % 5 else "待补课",
            }
        )
        quantities.append(
            {
                "清单编号": f"QDL-2026-{idx + 1:03d}",
                "清单名称": ["电缆敷设", "高压柜安装", "接地系统", "电气试验"][idx % 4],
                "单位": ["米", "台", "项", "回路"][idx % 4],
                "合同工程量": 100 + idx * 30,
                "本期完成": 20 + idx * 3,
                "累计完成": int((100 + idx * 30) * project["output_progress"]),
                "监理确认": "已确认" if idx % 3 else "待确认",
                "甲方确认": "已确认" if idx % 4 else "待确认",
                "是否计入产值": "是" if idx % 4 else "否",
            }
        )
        changes.append(
            {
                "签证编号": f"VISA-2026-{idx + 1:03d}",
                "所属项目": project["project_name"],
                "变更原因": ["现场路径调整", "建设单位新增负荷", "设计图纸优化"][idx % 3],
                "变更金额": project["contract_amount"] * (0.005 + idx % 4 * 0.002),
                "影响工期": f"{idx % 6 + 1} 天",
                "审批状态": ["审批中", "已通过", "待提交"][idx % 3],
                "关联资料": "签证单、现场照片、工程量确认单",
            }
        )
    photos = pd.DataFrame({"所属项目": active["project_name"], "照片类型": "现场照片", "拍摄部位": "施工现场", "上传状态": "已上传"})
    return {
        "施工日志": pd.DataFrame(logs),
        "班组管理": pd.DataFrame(teams),
        "人员进退场": pd.DataFrame(teams),
        "班前会": pd.DataFrame({"所属项目": active["project_name"], "会议主题": "班前安全技术交底", "参会人数": 10, "记录状态": "已记录"}),
        "现场照片": photos,
        "工序进度": progress,
        "工程量确认": pd.DataFrame(quantities),
        "签证变更": pd.DataFrame(changes),
    }


setup_page("施工现场中心")
init_session_state()
role = render_sidebar()
render_page_header("施工现场中心", "模拟工程现场过程管理，包括日志、班组、进退场、班前会、照片、工序、工程量和签证变更。")

projects = get_dataset("projects")
progress = get_dataset("progress")
tables = build_site_tables(projects, progress)
labels = ["施工日志", "班组管理", "人员进退场", "班前会", "现场照片", "工序进度", "工程量确认", "签证变更"]
tabs = st.tabs(labels)
for label, tab in zip(labels, tabs):
    with tab:
        render_filterable_table(to_display_df(tables[label]), label, height=360)

render_business_note("施工现场中心把现场过程数据和项目产值确认关联起来，后续可扩展移动端填报、照片水印、定位和监理确认。")

