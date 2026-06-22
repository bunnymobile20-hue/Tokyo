"""
Sistema Siberian — Normalizers
Convert raw API responses to TokyoOS internal format.
Never invents data. Always marks validation_status.
"""
from datetime import datetime, timezone


def normalize_generic(raw_data, scope="grupsbunny", category="unknown"):
    return {
        "success": True,
        "source": "sistema_siberian_api",
        "mode": "read_only",
        "validation_status": "pending_validation",
        "scope": scope,
        "category": category,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "raw_available": True,
        "data": raw_data,
        "warnings": [],
        "_token_exposed": False,
    }


def normalize_company(company_data, scope="sistema_siberian"):
    result = normalize_generic(company_data, scope, "company")
    if not isinstance(company_data, dict):
        result["warnings"].append("company_data is not a dict")
        return result
    result["data"] = {
        "id": company_data.get("id"),
        "name": company_data.get("name") or company_data.get("company_name"),
        "type": company_data.get("type"),
        "status": company_data.get("status"),
        "raw": company_data,
    }
    if not result["data"]["name"]:
        result["warnings"].append("company_name_missing")
    return result


def normalize_store(store_data, scope="bunny_dreams"):
    result = normalize_generic(store_data, scope, "store")
    if not isinstance(store_data, dict):
        result["warnings"].append("store_data is not a dict")
        return result
    store_scope = store_data.get("scope") or store_data.get("store_scope")
    store_name = store_data.get("name") or store_data.get("store_name")
    result["data"] = {
        "id": store_data.get("id"),
        "name": store_name,
        "scope": store_scope,
        "status": store_data.get("status"),
        "raw": store_data,
    }
    if not store_scope or store_scope not in ("riverside", "teresina", "bunny_dreams"):
        result["warnings"].append("store_scope_missing — impossible to attribute to specific store")
    if not store_name:
        result["warnings"].append("store_name_missing")
    return result


def normalize_sale(sale_data, store_scope=None):
    scope = store_scope or "bunny_dreams"
    result = normalize_generic(sale_data, scope, "sale")
    if not isinstance(sale_data, dict):
        result["warnings"].append("sale_data is not a dict")
        return result
    result["data"] = {
        "id": sale_data.get("id"),
        "store": sale_data.get("store") or sale_data.get("store_scope") or store_scope,
        "amount": sale_data.get("amount") or sale_data.get("total"),
        "date": sale_data.get("date") or sale_data.get("sale_date"),
        "status": sale_data.get("status"),
        "raw": sale_data,
    }
    if not result["data"]["store"] or result["data"]["store"] not in ("riverside", "teresina"):
        result["warnings"].append("store_scope_missing — sale cannot be attributed to specific store")
    return result


def normalize_finance_entry(entry_data, scope="grupsbunny"):
    result = normalize_generic(entry_data, scope, "finance")
    if not isinstance(entry_data, dict):
        result["warnings"].append("entry_data is not a dict")
        return result
    result["data"] = {
        "id": entry_data.get("id"),
        "type": entry_data.get("type"),
        "amount": entry_data.get("amount"),
        "date": entry_data.get("date"),
        "category": entry_data.get("category"),
        "scope": entry_data.get("scope") or scope,
        "raw": entry_data,
    }
    if not result["data"].get("scope"):
        result["warnings"].append("scope_missing")
    return result


def normalize_list(raw_list, normalizer_fn, scope=None, **kwargs):
    if not isinstance(raw_list, list):
        return {
            "success": True,
            "source": "sistema_siberian_api",
            "mode": "read_only",
            "validation_status": "pending_validation",
            "scope": scope or "grupsbunny",
            "received_at": datetime.now(timezone.utc).isoformat(),
            "data": [],
            "warnings": ["API response was not a list"],
            "_token_exposed": False,
        }
    results = []
    warnings = []
    for item in raw_list:
        normalized = normalizer_fn(item, scope=scope, **kwargs) if scope else normalizer_fn(item, **kwargs)
        results.append(normalized.get("data", item))
        warnings.extend(normalized.get("warnings", []))
    return {
        "success": True,
        "source": "sistema_siberian_api",
        "mode": "read_only",
        "validation_status": "pending_validation",
        "scope": scope or "grupsbunny",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "data": results,
        "count": len(results),
        "warnings": warnings,
        "_token_exposed": False,
    }
