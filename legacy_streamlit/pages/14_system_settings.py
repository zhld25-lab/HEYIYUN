from __future__ import annotations

import pandas as pd
import streamlit as st

from components.data_table import render_filterable_table
from components.layout import render_business_note, render_page_header, setup_page
from components.sidebar import render_sidebar
from config.industry_config import DOCUMENT_TYPES, MATERIAL_CATEGORIES, PROJECT_STATUSES, RISK_TYPES
from config.menu_config import MENU_ITEMS
from config.role_config import ROLE_MODULES, ROLE_USERS, ROLES
from services.permission_service import can_view_finance, get_visible_modules_by_role
from utils.session_state import init_session_state


setup_page("系统设置")
init_session_state()
role = render_sidebar()
render_page_header("系统设置", "模拟企业后台配置，包括用户、角色、权限、组织架构、菜单、数据字典、审批流程和日志。")

if role != "系统管理员":
    st.warning("当前不是系统管理员角色，仅展示配置样例。")

tabs = st.tabs(["用户管理", "角色管理", "权限管理", "组织架构", "菜单配置", "数据字典", "审批流程配置", "操作日志", "登录日志"])
with tabs[0]:
    users = pd.DataFrame([{"角色": r, "模拟用户": ROLE_USERS.get(r), "状态": "启用"} for r in ROLES])
    render_filterable_table(users)
with tabs[1]:
    roles = pd.DataFrame([{"角色": r, "可见模块": "、".join(get_visible_modules_by_role(r)), "可看金额": can_view_finance(r)} for r in ROLES])
    render_filterable_table(roles)
with tabs[2]:
    permissions = pd.DataFrame(
        [
            {"角色": "普通员工", "权限说明": "可看项目名称、状态和进度，金额显示为 ***"},
            {"角色": "项目经理", "权限说明": "可看项目、进度、施工、安全质量、材料、设备和自己项目成本汇总"},
            {"角色": "财务负责人", "权限说明": "可看合同、成本、付款、回款、发票和利润"},
            {"角色": "总经理", "权限说明": "可看全部模块和全部经营数据"},
            {"角色": "系统管理员", "权限说明": "可配置用户、角色、权限、菜单和日志"},
        ]
    )
    render_filterable_table(permissions)
with tabs[3]:
    org = pd.DataFrame({"部门": ["总经办", "工程管理部", "采购物资部", "财务部", "安全质量部", "资料档案部"], "负责人": ["周总", "王工", "赵经理", "林会计", "刘工", "吴工"]})
    render_filterable_table(org)
with tabs[4]:
    menu = pd.DataFrame(MENU_ITEMS, columns=["菜单名称", "页面文件"])
    render_filterable_table(menu)
with tabs[5]:
    dictionary = pd.DataFrame(
        {
            "字典类型": ["项目状态", "风险类型", "材料分类", "资料分类"],
            "字典值": ["、".join(PROJECT_STATUSES), "、".join(RISK_TYPES), "、".join(MATERIAL_CATEGORIES[:8]) + "...", "、".join(DOCUMENT_TYPES[:8]) + "..."],
        }
    )
    render_filterable_table(dictionary)
with tabs[6]:
    flow = pd.DataFrame({"节点顺序": [1, 2, 3, 4, 5, 6], "节点名称": ["发起人", "部门负责人", "项目经理", "财务负责人", "总经理", "完成"], "超时时限": ["-", "2天", "2天", "2天", "3天", "-"]})
    render_filterable_table(flow)
with tabs[7]:
    logs = pd.DataFrame({"时间": ["2026-06-01 09:00", "2026-06-01 09:15"], "操作人": ["系统管理员-陈工", "财务负责人-林会计"], "操作": ["调整角色权限", "导出成本台账"], "结果": ["成功", "成功"]})
    render_filterable_table(logs)
with tabs[8]:
    login_logs = pd.DataFrame({"登录时间": ["2026-06-01 08:30", "2026-06-01 08:42"], "用户": ["总经理-周总", "项目经理-王工"], "登录方式": ["模拟登录", "模拟登录"], "状态": ["成功", "成功"]})
    render_filterable_table(login_logs)

render_business_note("系统设置用于展示权限和后台配置思路，当前版本不接入真实认证，角色切换通过 session_state 模拟。")

