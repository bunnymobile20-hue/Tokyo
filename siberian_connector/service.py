"""
Sistema Siberian — Service Layer
Coordinates client calls, normalization, and audit logging.
Always read-only. Never writes to external API.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import os

from .client import (
    is_configured, get_config, get_health, get_companies,
    get_stores, get_sales_summary, get_finance_summary,
    get_products_summary, get_stock_summary,
)

AUDIT_DIR = Path(os.getenv("TOKYO_DATA_DIR", str(Path(__file__).parent.parent / "data"))) / "audit"
AUDIT_FILE = AUDIT_DIR / "siberian_api_readonly.jsonl"


def _audit(event, details=None):
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "details": details or {},
    }
    try:
        with open(AUDIT_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def get_status():
    _audit("siberian_status_checked", {"configured": is_configured()})
    cfg = get_config()
    return {
        "success": True,
        "configured": is_configured(),
        "status": "not_configured" if not is_configured() else "configured",
        "mode": cfg["mode"],
        "safe_mode": True,
        "config": {
            "base_url_configured": cfg["base_url_configured"],
            "api_key_configured": cfg["api_key_configured"],
            "api_token_configured": cfg["api_token_configured"],
            "has_auth": cfg["has_auth"],
        },
        "issues": [] if is_configured() else [
            "SIBERIAN_ENABLED=false — connector disabled",
            "SIBERIAN_API_BASE_URL not configured",
            "No auth configured",
        ],
        "message": "Sistema Siberian configurado em modo read_only." if is_configured() else "Sistema Siberian nao configurado.",
        "_token_exposed": False,
    }


def check_health():
    _audit("siberian_health_checked")
    if not is_configured():
        return {"success": True, "status": "not_configured", "health": None, "source": "pending_api", "mode": "read_only", "_token_exposed": False}
    result = get_health()
    _audit("siberian_health_checked", {"online": result["success"]})
    return result


def fetch_companies():
    _audit("siberian_get_requested", {"path": "/api/companies"})
    if not is_configured():
        return {"success": True, "status": "not_configured", "data": None, "source": "pending_api", "mode": "read_only", "_token_exposed": False}
    result = get_companies()
    _audit("siberian_get_success" if result["success"] else "siberian_get_failed", {"status": result["status"]})
    return result


def fetch_stores():
    _audit("siberian_get_requested", {"path": "/api/stores"})
    if not is_configured():
        return {"success": True, "status": "not_configured", "data": None, "source": "pending_api", "mode": "read_only", "_token_exposed": False}
    result = get_stores()
    _audit("siberian_get_success" if result["success"] else "siberian_get_failed", {"status": result["status"]})
    return result


def fetch_sales_summary():
    _audit("siberian_get_requested", {"path": "/api/sales/summary"})
    if not is_configured():
        return {"success": True, "status": "not_configured", "data": None, "source": "pending_api", "mode": "read_only", "_token_exposed": False}
    result = get_sales_summary()
    _audit("siberian_get_success" if result["success"] else "siberian_get_failed", {"status": result["status"]})
    return result


def fetch_finance_summary():
    _audit("siberian_get_requested", {"path": "/api/finance/summary"})
    if not is_configured():
        return {"success": True, "status": "not_configured", "data": None, "source": "pending_api", "mode": "read_only", "_token_exposed": False}
    result = get_finance_summary()
    _audit("siberian_get_success" if result["success"] else "siberian_get_failed", {"status": result["status"]})
    return result


def fetch_products_summary():
    _audit("siberian_get_requested", {"path": "/api/products/summary"})
    if not is_configured():
        return {"success": True, "status": "not_configured", "data": None, "source": "pending_api", "mode": "read_only", "_token_exposed": False}
    result = get_products_summary()
    _audit("siberian_get_success" if result["success"] else "siberian_get_failed", {"status": result["status"]})
    return result


def fetch_stock_summary():
    _audit("siberian_get_requested", {"path": "/api/stock/summary"})
    if not is_configured():
        return {"success": True, "status": "not_configured", "data": None, "source": "pending_api", "mode": "read_only", "_token_exposed": False}
    result = get_stock_summary()
    _audit("siberian_get_success" if result["success"] else "siberian_get_failed", {"status": result["status"]})
    return result


def get_schema():
    _audit("siberian_schema_checked")
    return {
        "success": True,
        "source": "siberian_connector",
        "mode": "read_only",
        "capabilities": [
            {"id": "companies", "method": "GET", "path": "/api/companies", "safe_method": True, "read_only": True},
            {"id": "stores", "method": "GET", "path": "/api/stores", "safe_method": True, "read_only": True},
            {"id": "sales", "method": "GET", "path": "/api/sales/summary", "safe_method": True, "read_only": True},
            {"id": "finance", "method": "GET", "path": "/api/finance/summary", "safe_method": True, "read_only": True},
            {"id": "products", "method": "GET", "path": "/api/products/summary", "safe_method": True, "read_only": True},
            {"id": "stock", "method": "GET", "path": "/api/stock/summary", "safe_method": True, "read_only": True},
            {"id": "customers", "status": "planned"},
            {"id": "users", "status": "planned"},
            {"id": "reports", "status": "planned"},
            {"id": "recurrence", "status": "planned"},
            {"id": "support", "status": "planned"},
        ],
        "operations_allowed": ["GET"],
        "operations_blocked": ["POST", "PUT", "PATCH", "DELETE"],
        "configured": is_configured(),
        "_token_exposed": False,
    }


def get_real_api_readiness():
    """Pre-Real API Gate — checks if Siberian is ready for actual connection."""
    cfg = get_config()
    ready = is_configured()
    issues = []
    next_step = ""
    if ready:
        next_step = "Executar Phase 3B real handshake read-only. Sistema Siberian configurado e pronto."
    elif not cfg["enabled"]:
        next_step = "Configure SIBERIAN_ENABLED=true, SIBERIAN_API_BASE_URL e credenciais no .env local, sem expor tokens."
    else:
        issues = [i for i in [not cfg["base_url_configured"] and "SIBERIAN_API_BASE_URL missing",
                              not cfg["has_auth"] and "No auth credentials configured"] if i]
        next_step = "Corrija as configuracoes pendentes no .env e reinicie."

    return {
        "success": True,
        "ready_for_real_api": ready,
        "enabled": cfg["enabled"],
        "base_url_configured": cfg["base_url_configured"],
        "auth_configured": cfg["has_auth"],
        "mode": cfg["mode"],
        "external_write_enabled": False,
        "allowed_methods": ["GET"],
        "blocked_methods": ["POST", "PUT", "PATCH", "DELETE"],
        "next_step": next_step,
        "issues": issues,
        "_token_exposed": False,
    }
