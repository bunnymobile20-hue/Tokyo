def calculate_confidence(missing_fields: int, total_fields: int) -> str:
    if total_fields == 0:
        return "none"
    ratio = (total_fields - missing_fields) / total_fields
    if ratio == 1.0:
        return "high"
    elif ratio >= 0.7:
        return "medium"
    return "low"
