from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def get_all_equipment() -> pd.DataFrame:
    return get_dataset("equipment")


def get_equipment_by_project(project_id: str) -> pd.DataFrame:
    equipment = get_all_equipment()
    return equipment[equipment["project_id"] == project_id].copy()


def detect_equipment_risks(equipment: pd.DataFrame | None = None) -> pd.DataFrame:
    equipment = equipment if equipment is not None else get_all_equipment()
    if equipment.empty:
        return pd.DataFrame()
    return equipment[
        (equipment["current_status"].isin(["闲置", "待归还"]))
        | (equipment["maintenance_status"] == "超期未保养")
        | (equipment["repair_status"] == "维修中")
    ].copy()

