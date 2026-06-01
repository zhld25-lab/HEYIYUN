from __future__ import annotations

import pandas as pd

from data.data_loader import get_dataset


def get_all_documents() -> pd.DataFrame:
    return get_dataset("documents")


def get_documents_by_project(project_id: str) -> pd.DataFrame:
    documents = get_all_documents()
    return documents[documents["project_id"] == project_id].copy()


def get_document_completion_by_project() -> pd.DataFrame:
    documents = get_all_documents()
    grouped = documents.groupby("project_name", as_index=False).agg(
        total=("id", "count"),
        missing=("is_missing", "sum"),
        required=("is_required", "sum"),
    )
    grouped["completion_rate"] = 1 - grouped["missing"] / grouped["total"]
    return grouped.sort_values("completion_rate")


def get_missing_documents() -> pd.DataFrame:
    documents = get_all_documents()
    return documents[documents["is_missing"]].copy()

