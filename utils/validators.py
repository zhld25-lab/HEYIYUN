def ensure_required_columns(dataframe, required_columns):
    missing = [col for col in required_columns if col not in dataframe.columns]
    if missing:
        raise ValueError(f"缺少必要字段: {', '.join(missing)}")
    return True

