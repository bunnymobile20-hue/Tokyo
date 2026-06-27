from typing import List

def check_missing_fields(payload: dict, required_keys: List[str]) -> List[str]:
    missing = []
    if not isinstance(payload, dict):
        return required_keys
    for key in required_keys:
        if key not in payload or payload[key] is None:
            missing.append(key)
    return missing

def generate_warnings(missing_fields: List[str]) -> List[str]:
    warnings = []
    if missing_fields:
        warnings.append(f"Data incomplete. Missing critical fields: {', '.join(missing_fields)}")
    return warnings
