from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd

from config.industry_config import (
    DOCUMENT_TYPES,
    EQUIPMENT_TYPES,
    MATERIAL_CATEGORIES,
    PROJECT_STATUSES,
    PROJECT_TYPES,
    RISK_TYPES,
    VOLTAGE_LEVELS,
)
from data.mock_contracts import APPROVAL_STATUSES, CONTRACT_STATUSES, CONTRACT_TYPES
from data.mock_costs import COST_TYPES, INVOICE_STATUSES, PAYMENT_STATUSES
from data.mock_documents import DOCUMENT_STATUSES
from data.mock_equipment import EQUIPMENT_OWNERS, EQUIPMENT_STATUSES
from data.mock_finance import FINANCE_TYPES, INVOICE_TYPES
from data.mock_materials import MATERIAL_SPECS
from data.mock_progress import PROGRESS_NODES
from data.mock_projects import PROJECT_MANAGERS, PROJECT_NAME_SEEDS
from data.mock_risks import RISK_LEVELS, RISK_STATUSES
from data.mock_safety_quality import ISSUE_LEVELS, QUALITY_TYPES, SAFETY_TYPES
from data.mock_workflows import WORKFLOW_NODES, WORKFLOW_TYPES

BASE_DATE = pd.Timestamp("2025-01-01")
TODAY = pd.Timestamp("2026-06-01")
RNG = np.random.default_rng(20260601)


def _money(value: float) -> float:
    return float(round(value, 2))


def _risk_from_project(row: dict[str, Any]) -> str:
    triggers = 0
    if row["actual_cost"] > row["target_cost"] * 1.1:
        triggers += 1
    if row["output_progress"] - row["collection_progress"] > 0.2:
        triggers += 1
    if row["document_completion"] < 0.8:
        triggers += 1
    if row["planned_end"] < TODAY and row["status"] not in {"已完工", "结算中"}:
        triggers += 1
    if row["status"] == "暂停":
        triggers += 1
    if triggers >= 4:
        return "严重"
    if triggers >= 3:
        return "高"
    if triggers >= 1:
        return "中"
    return "低"


def generate_projects() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    status_cycle = ["施工中", "报装中", "施工中", "验收中", "结算中", "施工中", "施工中", "已完工", "暂停", "立项"]
    for idx, name in enumerate(PROJECT_NAME_SEEDS, start=1):
        status = status_cycle[(idx - 1) % len(status_cycle)]
        start = BASE_DATE + pd.Timedelta(days=idx * 21)
        duration = int(RNG.integers(120, 360))
        planned_end = start + pd.Timedelta(days=duration)
        status_progress = {
            "立项": 0.06,
            "报装中": 0.18,
            "施工中": float(RNG.uniform(0.36, 0.78)),
            "验收中": float(RNG.uniform(0.82, 0.92)),
            "结算中": float(RNG.uniform(0.92, 0.99)),
            "已完工": 1.0,
            "暂停": float(RNG.uniform(0.25, 0.55)),
        }[status]
        amount = _money(float(RNG.integers(280, 6800)) * 10000)
        if "220kV" in name:
            amount = _money(float(RNG.integers(8000, 15000)) * 10000)
        if "临时用电" in name:
            amount = _money(float(RNG.integers(120, 500)) * 10000)
        target_cost = _money(amount * float(RNG.uniform(0.72, 0.86)))
        cost_factor = float(RNG.uniform(0.78, 1.08))
        if idx in {3, 6, 9, 14, 18}:
            cost_factor = float(RNG.uniform(1.12, 1.32))
        actual_cost = _money(target_cost * cost_factor * max(status_progress, 0.22))
        if status in {"结算中", "已完工"}:
            actual_cost = _money(target_cost * float(RNG.uniform(0.92, 1.08)))
        collection_progress = max(0.02, status_progress - float(RNG.uniform(0.02, 0.28)))
        if idx in {4, 7, 12, 17}:
            collection_progress = max(0.03, status_progress - float(RNG.uniform(0.25, 0.45)))
        if status == "已完工":
            collection_progress = float(RNG.uniform(0.82, 0.98))
        received_amount = _money(amount * min(collection_progress, 1))
        paid_amount = _money(actual_cost * float(RNG.uniform(0.55, 0.92)))
        document_completion = float(RNG.uniform(0.58, 0.98))
        if status in {"结算中", "已完工"}:
            document_completion = float(RNG.uniform(0.86, 1.0))
        if idx in {6, 10, 15}:
            document_completion = float(RNG.uniform(0.45, 0.72))
        row = {
            "id": f"P{idx:03d}",
            "project_no": f"PEP-2026-{idx:03d}",
            "project_name": name,
            "project_type": PROJECT_TYPES[(idx - 1) % len(PROJECT_TYPES)],
            "voltage_level": VOLTAGE_LEVELS[(idx + 1) % len(VOLTAGE_LEVELS)],
            "address": f"示范城市第{idx}片区电力工程现场",
            "owner": f"示范建设单位{idx:02d}有限公司",
            "constructor": "华东示范电力工程有限公司",
            "designer": f"示范电力设计院{(idx % 4) + 1}所",
            "supervisor": f"示范监理咨询{(idx % 5) + 1}公司",
            "project_manager": PROJECT_MANAGERS[(idx - 1) % len(PROJECT_MANAGERS)],
            "status": status,
            "planned_start": start,
            "planned_end": planned_end,
            "actual_start": start + pd.Timedelta(days=int(RNG.integers(0, 12))),
            "actual_end": planned_end + pd.Timedelta(days=int(RNG.integers(-20, 45))) if status in {"已完工", "结算中"} else pd.NaT,
            "contract_amount": amount,
            "target_cost": target_cost,
            "actual_cost": actual_cost,
            "received_amount": received_amount,
            "paid_amount": paid_amount,
            "output_progress": round(status_progress, 3),
            "collection_progress": round(received_amount / amount, 3),
            "document_completion": round(document_completion, 3),
            "description": f"{name}，覆盖供电报装、设计采购、现场施工、验收送电、结算归档全过程。",
        }
        row["cost_ratio"] = round(row["actual_cost"] / row["target_cost"], 3)
        row["profit"] = _money(row["received_amount"] - row["actual_cost"])
        row["expected_profit"] = _money(row["contract_amount"] - row["actual_cost"])
        row["profit_rate"] = round(row["expected_profit"] / row["contract_amount"], 3)
        row["risk_level"] = _risk_from_project(row)
        rows.append(row)
    return pd.DataFrame(rows)


def generate_contracts(projects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    parties = ["示范成套电气有限公司", "示范电缆集团", "示范建设劳务有限公司", "示范设备租赁有限公司", "示范材料供应链有限公司"]
    for pidx, project in projects.iterrows():
        project_id = project["id"]
        contract_specs = [
            ("承包合同", project["contract_amount"], project["owner"], "华东示范电力工程有限公司"),
            ("采购合同", project["target_cost"] * 0.34, "华东示范电力工程有限公司", parties[pidx % len(parties)]),
            ("分包合同", project["target_cost"] * 0.26, "华东示范电力工程有限公司", parties[(pidx + 2) % len(parties)]),
        ]
        if pidx % 2 == 0:
            contract_specs.append(("设备租赁合同", project["target_cost"] * 0.08, "华东示范电力工程有限公司", parties[(pidx + 3) % len(parties)]))
        if pidx % 3 == 0:
            contract_specs.append(("周材租赁合同", project["target_cost"] * 0.05, "华东示范电力工程有限公司", parties[(pidx + 4) % len(parties)]))
        for cidx, (ctype, amount, party_a, party_b) in enumerate(contract_specs, start=1):
            serial = len(rows) + 1
            settlement = _money(amount * float(RNG.uniform(0.92, 1.08)))
            invoice = _money(settlement * float(RNG.uniform(0.55, 1.0)))
            if ctype == "承包合同":
                received = project["received_amount"]
                paid = 0.0
                receivable = max(_money(settlement - received), 0)
                payable = 0.0
            else:
                received = 0.0
                paid = _money(settlement * float(RNG.uniform(0.28, 0.86)) * max(project["output_progress"], 0.2))
                receivable = 0.0
                payable = max(_money(settlement - paid), 0)
            rows.append(
                {
                    "id": f"C{serial:04d}",
                    "contract_no": f"HT-2026-{serial:04d}",
                    "contract_name": f"{project['project_name']} {ctype}",
                    "contract_type": ctype,
                    "project_id": project_id,
                    "project_name": project["project_name"],
                    "party_a": party_a,
                    "party_b": party_b,
                    "contract_amount": _money(amount),
                    "settlement_amount": settlement,
                    "invoice_amount": invoice,
                    "received_amount": _money(received),
                    "paid_amount": _money(paid),
                    "receivable": receivable,
                    "payable": payable,
                    "contract_status": CONTRACT_STATUSES[(serial + cidx) % len(CONTRACT_STATUSES)],
                    "approval_status": APPROVAL_STATUSES[(serial + pidx) % len(APPROVAL_STATUSES)],
                    "archive_status": "已归档" if project["status"] in {"结算中", "已完工"} and cidx == 1 else ("未归档" if cidx % 4 == 0 else "归档中"),
                    "cost_category": "收入合同" if ctype == "承包合同" else ("材料成本" if ctype == "采购合同" else "分包/租赁成本"),
                    "sign_date": project["planned_start"] + pd.Timedelta(days=15 + cidx * 7),
                }
            )
    return pd.DataFrame(rows)


def generate_costs(projects: pd.DataFrame, contracts: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    vendors = ["示范电缆集团", "示范劳务一队", "示范吊装服务部", "示范运输有限公司", "示范机具租赁站"]
    for _, project in projects.iterrows():
        project_contracts = contracts[(contracts["project_id"] == project["id"]) & (contracts["contract_type"] != "承包合同")]
        for cidx in range(6):
            serial = len(rows) + 1
            cost_type = COST_TYPES[(serial + cidx) % len(COST_TYPES)]
            amount = _money(project["actual_cost"] * float(RNG.uniform(0.025, 0.12)))
            contract_id = project_contracts.iloc[cidx % len(project_contracts)]["id"] if not project_contracts.empty else ""
            rows.append(
                {
                    "id": f"CO{serial:04d}",
                    "cost_no": f"CB-2026-{serial:04d}",
                    "cost_type": cost_type,
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "contract_id": contract_id,
                    "supplier": vendors[serial % len(vendors)],
                    "amount": amount,
                    "occur_date": project["planned_start"] + pd.Timedelta(days=int(RNG.integers(20, 260))),
                    "handler": PROJECT_MANAGERS[serial % len(PROJECT_MANAGERS)],
                    "approval_status": APPROVAL_STATUSES[serial % len(APPROVAL_STATUSES)],
                    "invoice_status": INVOICE_STATUSES[serial % len(INVOICE_STATUSES)],
                    "payment_status": PAYMENT_STATUSES[serial % len(PAYMENT_STATUSES)],
                    "is_project_cost": True,
                }
            )
    return pd.DataFrame(rows)


def generate_materials(projects: pd.DataFrame, contracts: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    suppliers = ["示范电缆集团", "示范成套电气有限公司", "示范配网物资有限公司", "示范五金机电有限公司"]
    for _, project in projects.iterrows():
        purchase_contracts = contracts[(contracts["project_id"] == project["id"]) & (contracts["contract_type"] == "采购合同")]
        purchase_contract_id = purchase_contracts.iloc[0]["id"] if not purchase_contracts.empty else ""
        for midx in range(5):
            serial = len(rows) + 1
            category = MATERIAL_CATEGORIES[(serial + midx) % len(MATERIAL_CATEGORIES)]
            specs = MATERIAL_SPECS.get(category, [f"{category}-标准规格", f"{category}-增强规格"])
            qty = int(RNG.integers(8, 320))
            budget_price = float(RNG.integers(80, 18000))
            price_factor = float(RNG.uniform(0.88, 1.18))
            if serial % 11 == 0:
                price_factor = float(RNG.uniform(1.2, 1.36))
            purchase_price = _money(budget_price * price_factor)
            stock_qty = int(qty * float(RNG.uniform(0.0, 0.8)))
            rows.append(
                {
                    "id": f"M{serial:04d}",
                    "material_code": f"WL-{serial:04d}",
                    "material_name": category,
                    "category": category,
                    "specification": specs[serial % len(specs)],
                    "unit": "米" if "电缆" in category or "管材" in category else "台" if category in {"环网柜", "箱式变电站", "高压柜", "低压柜", "变压器"} else "批",
                    "quantity": qty,
                    "budget_unit_price": _money(budget_price),
                    "purchase_unit_price": purchase_price,
                    "total_amount": _money(qty * purchase_price),
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "supplier": suppliers[serial % len(suppliers)],
                    "purchase_contract_id": purchase_contract_id,
                    "delivery_status": ["未到货", "部分到货", "已到货"][serial % 3],
                    "warehouse_status": ["未入库", "部分入库", "已入库"][serial % 3],
                    "usage_status": ["未领用", "部分领用", "已领用"][serial % 3],
                    "stock_quantity": stock_qty,
                    "safe_stock": max(5, int(qty * 0.12)),
                    "is_over_price": purchase_price > budget_price * 1.08,
                    "is_shortage": stock_qty < max(5, int(qty * 0.12)),
                }
            )
    return pd.DataFrame(rows)


def generate_equipment(projects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, project in projects.head(15).iterrows():
        for eidx in range(2):
            serial = len(rows) + 1
            equipment_name = EQUIPMENT_TYPES[serial % len(EQUIPMENT_TYPES)]
            rental_price = _money(float(RNG.integers(300, 4500)))
            days = int(RNG.integers(15, 90))
            rows.append(
                {
                    "id": f"E{serial:04d}",
                    "equipment_no": f"SB-2026-{serial:04d}",
                    "equipment_name": equipment_name,
                    "specification": f"{equipment_name}-示范型号{(serial % 5) + 1}",
                    "owner_unit": EQUIPMENT_OWNERS[serial % len(EQUIPMENT_OWNERS)],
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "current_status": EQUIPMENT_STATUSES[serial % len(EQUIPMENT_STATUSES)],
                    "use_start": project["planned_start"] + pd.Timedelta(days=int(RNG.integers(20, 80))),
                    "use_end": project["planned_start"] + pd.Timedelta(days=int(RNG.integers(90, 260))),
                    "rental_price": rental_price,
                    "rental_amount": _money(rental_price * days),
                    "maintenance_status": "超期未保养" if serial % 9 == 0 else "正常",
                    "repair_status": "维修中" if serial % 13 == 0 else "正常",
                    "responsible_person": PROJECT_MANAGERS[serial % len(PROJECT_MANAGERS)],
                }
            )
    return pd.DataFrame(rows)


def generate_progress(projects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, project in projects.iterrows():
        completed_nodes = int(round(project["output_progress"] * len(PROGRESS_NODES)))
        for nidx, node in enumerate(PROGRESS_NODES, start=1):
            plan_start = project["planned_start"] + pd.Timedelta(days=(nidx - 1) * 18)
            plan_finish = plan_start + pd.Timedelta(days=14)
            is_done = nidx <= completed_nodes
            delay = int(RNG.integers(0, 28)) if is_done and (project["risk_level"] in {"高", "严重"} and nidx % 4 == 0) else int(RNG.integers(-5, 8))
            actual_finish = plan_finish + pd.Timedelta(days=delay) if is_done else pd.NaT
            rows.append(
                {
                    "id": f"PN-{project['id']}-{nidx:02d}",
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "node_name": node,
                    "planned_start": plan_start,
                    "planned_finish": plan_finish,
                    "actual_finish": actual_finish,
                    "owner": PROJECT_MANAGERS[(nidx + len(rows)) % len(PROJECT_MANAGERS)],
                    "status": "已完成" if is_done else ("进行中" if nidx == completed_nodes + 1 else "未开始"),
                    "is_delayed": bool(is_done and pd.notna(actual_finish) and actual_finish > plan_finish),
                    "attachment": f"{node}记录.pdf" if is_done else "",
                }
            )
    return pd.DataFrame(rows)


def generate_finance(projects: pd.DataFrame, contracts: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, project in projects.iterrows():
        main_contract = contracts[(contracts["project_id"] == project["id"]) & (contracts["contract_type"] == "承包合同")].iloc[0]
        for fidx, ftype in enumerate(FINANCE_TYPES, start=1):
            serial = len(rows) + 1
            if ftype == "回款":
                direction = "收入"
                amount = _money(project["received_amount"] * float(RNG.uniform(0.18, 0.42)))
            elif ftype == "付款":
                direction = "支出"
                amount = _money(project["paid_amount"] * float(RNG.uniform(0.15, 0.36)))
            elif ftype == "发票":
                direction = "收入" if serial % 2 else "支出"
                amount = _money(main_contract["invoice_amount"] * float(RNG.uniform(0.2, 0.6)))
            elif ftype == "保证金":
                direction = "支出"
                amount = _money(project["contract_amount"] * 0.03)
            else:
                direction = "计划"
                amount = _money(project["contract_amount"] * float(RNG.uniform(0.05, 0.16)))
            rows.append(
                {
                    "id": f"F{serial:04d}",
                    "finance_no": f"ZJ-2026-{serial:04d}",
                    "finance_type": ftype,
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "contract_id": main_contract["id"],
                    "counterparty": project["owner"] if direction == "收入" else "示范供应商/分包商",
                    "amount": amount,
                    "direction": direction,
                    "business_date": project["planned_start"] + pd.Timedelta(days=int(RNG.integers(30, 320))),
                    "invoice_type": INVOICE_TYPES[serial % len(INVOICE_TYPES)],
                    "invoice_status": ["未开票", "已开票", "已认证"][serial % 3],
                    "plan_status": ["按计划", "逾期", "提前"][serial % 3],
                }
            )
    return pd.DataFrame(rows)


def generate_workflows(projects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, project in projects.iterrows():
        for widx in range(3):
            serial = len(rows) + 1
            workflow_type = WORKFLOW_TYPES[(serial + widx) % len(WORKFLOW_TYPES)]
            current_node = WORKFLOW_NODES[(serial % (len(WORKFLOW_NODES) - 1))]
            arrival = TODAY - pd.Timedelta(days=int(RNG.integers(1, 12)))
            is_overdue = bool((TODAY - arrival).days > 5 and serial % 3 == 0)
            status = "审批中" if serial % 4 != 0 else ("已通过" if serial % 8 else "已驳回")
            rows.append(
                {
                    "id": f"W{serial:04d}",
                    "workflow_no": f"LC-2026-{serial:04d}",
                    "workflow_type": workflow_type,
                    "title": f"{project['project_name']} {workflow_type}",
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "initiator": PROJECT_MANAGERS[serial % len(PROJECT_MANAGERS)],
                    "current_node": current_node,
                    "current_handler": PROJECT_MANAGERS[(serial + 2) % len(PROJECT_MANAGERS)],
                    "start_time": arrival - pd.Timedelta(days=int(RNG.integers(1, 8))),
                    "arrival_time": arrival,
                    "is_overdue": is_overdue,
                    "approval_status": status,
                    "approval_result": "待处理" if status == "审批中" else status,
                    "approval_opinion": "资料基本完整，请按节点推进。" if status != "已驳回" else "补充合同附件后重新提交。",
                    "trace": "发起人:提交 > 部门负责人:通过 > 项目经理:处理中",
                }
            )
    return pd.DataFrame(rows)


def generate_safety_quality(projects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, project in projects.iterrows():
        for sqidx in range(3):
            serial = len(rows) + 1
            category = "安全" if serial % 2 else "质量"
            issue_type = SAFETY_TYPES[serial % len(SAFETY_TYPES)] if category == "安全" else QUALITY_TYPES[serial % len(QUALITY_TYPES)]
            closed = not (project["risk_level"] in {"高", "严重"} and serial % 3 == 0)
            rows.append(
                {
                    "id": f"SQ{serial:04d}",
                    "record_no": f"AQZL-2026-{serial:04d}",
                    "category": category,
                    "issue_type": issue_type,
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "issue_level": ISSUE_LEVELS[serial % len(ISSUE_LEVELS)],
                    "found_by": PROJECT_MANAGERS[serial % len(PROJECT_MANAGERS)],
                    "found_date": project["planned_start"] + pd.Timedelta(days=int(RNG.integers(40, 260))),
                    "responsible_person": PROJECT_MANAGERS[(serial + 1) % len(PROJECT_MANAGERS)],
                    "rectify_deadline": TODAY + pd.Timedelta(days=int(RNG.integers(-8, 18))),
                    "rectify_requirement": "按规范整改并上传整改前后照片及复查记录。",
                    "rectify_status": "已关闭" if closed else ("整改中" if serial % 2 else "逾期未整改"),
                    "review_result": "通过" if closed else "待复查",
                    "is_closed": closed,
                }
            )
    return pd.DataFrame(rows)


def generate_documents(projects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, project in projects.iterrows():
        for didx in range(6):
            serial = len(rows) + 1
            doc_type = DOCUMENT_TYPES[(serial + didx) % len(DOCUMENT_TYPES)]
            must = didx < 4
            missing = bool(must and project["document_completion"] < 0.8 and serial % 3 == 0)
            rows.append(
                {
                    "id": f"D{serial:04d}",
                    "document_no": f"ZL-2026-{serial:04d}",
                    "document_name": f"{project['project_name']} {doc_type}",
                    "document_type": doc_type,
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "uploader": PROJECT_MANAGERS[serial % len(PROJECT_MANAGERS)],
                    "upload_time": project["planned_start"] + pd.Timedelta(days=int(RNG.integers(10, 330))),
                    "audit_status": "缺失" if missing else DOCUMENT_STATUSES[serial % len(DOCUMENT_STATUSES)],
                    "is_required": must,
                    "is_missing": missing,
                    "version": f"V{(serial % 3) + 1}.0",
                    "file_path": "" if missing else f"/demo/files/{project['id']}/{serial:04d}.pdf",
                }
            )
    return pd.DataFrame(rows)


def generate_risks(projects: pd.DataFrame, workflows: pd.DataFrame, safety_quality: pd.DataFrame, documents: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, project in projects.iterrows():
        project_workflows = workflows[workflows["project_id"] == project["id"]]
        project_sq = safety_quality[safety_quality["project_id"] == project["id"]]
        project_docs = documents[documents["project_id"] == project["id"]]
        risk_candidates: list[tuple[str, str, str, str]] = []
        if project["planned_end"] < TODAY and project["status"] not in {"已完工", "结算中"}:
            risk_candidates.append(("工期风险", "高", "计划工期已到期但项目未完工", "重新编排施工计划并明确关键节点责任人"))
        if project["actual_cost"] > project["target_cost"] * 1.1:
            level = "严重" if project["actual_cost"] > project["target_cost"] * 1.25 else "高"
            risk_candidates.append(("成本风险", level, "实际成本超过目标成本控制线", "复核采购与分包结算，冻结非必要支出"))
        if project["output_progress"] - project["collection_progress"] > 0.2:
            risk_candidates.append(("资金风险", "高", "收款进度明显落后于产值进度", "推进工程量确认、发票和回款节点"))
        if project["document_completion"] < 0.8:
            level = "高" if project["document_completion"] < 0.6 else "中"
            risk_candidates.append(("资料风险", level, "项目必传资料完整率低于要求", "资料员按清单补齐报装、试验和竣工资料"))
        if project_workflows["is_overdue"].any():
            risk_candidates.append(("审批风险", "中", "存在超过规定处理时限的审批流程", "催办当前处理人并升级超时节点"))
        if (~project_sq["is_closed"]).sum() > 0:
            risk_candidates.append(("安全风险" if (project_sq["category"] == "安全").any() else "质量风险", "高", "安全质量问题未全部闭环", "责任人整改后提交复查资料"))
        if not risk_candidates:
            risk_candidates.append(("合同风险", "低", "项目处于正常执行状态，需持续关注合同归档", "按月复核合同、发票和结算资料"))
        for ridx, (rtype, level, reason, action) in enumerate(risk_candidates[:3], start=1):
            serial = len(rows) + 1
            rows.append(
                {
                    "id": f"R{serial:04d}",
                    "risk_no": f"FX-2026-{serial:04d}",
                    "risk_type": rtype,
                    "risk_level": level,
                    "project_id": project["id"],
                    "project_name": project["project_name"],
                    "trigger_reason": reason,
                    "risk_indicator": f"产值{project['output_progress']:.0%} / 收款{project['collection_progress']:.0%} / 成本比{project['cost_ratio']:.0%}",
                    "responsible_person": project["project_manager"],
                    "deadline": TODAY + pd.Timedelta(days=int(RNG.integers(3, 21))),
                    "recommended_action": action,
                    "current_status": RISK_STATUSES[(serial + ridx) % len(RISK_STATUSES)],
                    "is_closed": False if level in {"高", "严重"} else bool(serial % 2),
                }
            )
    while len(rows) < 60:
        project = projects.iloc[len(rows) % len(projects)]
        serial = len(rows) + 1
        rtype = RISK_TYPES[serial % len(RISK_TYPES)]
        level = RISK_LEVELS[serial % len(RISK_LEVELS)]
        rows.append(
            {
                "id": f"R{serial:04d}",
                "risk_no": f"FX-2026-{serial:04d}",
                "risk_type": rtype,
                "risk_level": level,
                "project_id": project["id"],
                "project_name": project["project_name"],
                "trigger_reason": f"{rtype}模拟监测指标触发预警",
                "risk_indicator": f"综合评分 {int(RNG.integers(45, 92))}",
                "responsible_person": project["project_manager"],
                "deadline": TODAY + pd.Timedelta(days=int(RNG.integers(2, 30))),
                "recommended_action": "责任部门复核数据并在系统内形成闭环记录",
                "current_status": RISK_STATUSES[serial % len(RISK_STATUSES)],
                "is_closed": bool(serial % 4 == 0),
            }
        )
    return pd.DataFrame(rows)


@lru_cache(maxsize=1)
def load_all_data() -> dict[str, pd.DataFrame]:
    projects = generate_projects()
    contracts = generate_contracts(projects)
    costs = generate_costs(projects, contracts)
    materials = generate_materials(projects, contracts)
    equipment = generate_equipment(projects)
    progress = generate_progress(projects)
    finance = generate_finance(projects, contracts)
    workflows = generate_workflows(projects)
    safety_quality = generate_safety_quality(projects)
    documents = generate_documents(projects)
    risks = generate_risks(projects, workflows, safety_quality, documents)
    return {
        "projects": projects,
        "contracts": contracts,
        "costs": costs,
        "materials": materials,
        "equipment": equipment,
        "progress": progress,
        "finance": finance,
        "workflows": workflows,
        "safety_quality": safety_quality,
        "documents": documents,
        "risks": risks,
    }


def get_dataset(name: str) -> pd.DataFrame:
    data = load_all_data()
    if name not in data:
        raise KeyError(f"未知数据集: {name}")
    return data[name].copy()

