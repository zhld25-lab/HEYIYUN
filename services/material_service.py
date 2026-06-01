from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def get_all_materials() -> pd.DataFrame:
    return get_dataset("materials")


def get_materials_by_project(project_id: str) -> pd.DataFrame:
    materials = get_all_materials()
    return materials[materials["project_id"] == project_id].copy()


def get_material_risks(materials: pd.DataFrame | None = None) -> pd.DataFrame:
    materials = materials if materials is not None else get_all_materials()
    if materials.empty:
        return pd.DataFrame()
    return materials[materials["is_over_price"] | materials["is_shortage"] | (materials["delivery_status"] != "已到货")].copy()


def get_supplier_ranking() -> pd.DataFrame:
    materials = get_all_materials()
    return materials.groupby("supplier", as_index=False)["total_amount"].sum().sort_values("total_amount", ascending=False)

