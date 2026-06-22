"""
Sistema Siberian API Client — Read-Only
Only GET requests. No external writes. Credentials never logged.
"""
import os
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone

logger = logging.getLogger("tokyoos.siberian")

SIBERIAN_ENABLED = os.getenv("SIBERIAN_ENABLED", "false").lower() in ("true", "1", "yes")
SIBERIAN_MODE = os.getenv("SIBERIAN_MODE", "read_only")
SIBERIAN_BASE_URL = os.getenv("SIBERIAN_API_BASE_URL", "").rstrip("/")
SIBERIAN_API_KEY = os.getenv("SIBERIAN_API_KEY", "")
SIBERIAN_API_TOKEN = os.getenv("SIBERIAN_API_TOKEN", "")
TIMEOUT_SECONDS = int(os.getenv("SIBERIAN_TIMEOUT", "15"))
MAX_RETRIES = int(os.getenv("SIBERIAN_MAX_RETRIES", "2"))


def get_config():
    return {
        "enabled": SIBERIAN_ENABLED,
        "mode": SIBERIAN_MODE,
        "base_url_configured": bool(SIBERIAN_BASE_URL),
        "api_key_configured": bool(SIBERIAN_API_KEY),
        "api_token_configured": bool(SIBERIAN_API_TOKEN),
        "has_auth": bool(SIBERIAN_API_KEY or SIBERIAN_API_TOKEN),
        "timeout": TIMEOUT_SECONDS,
        "max_retries": MAX_RETRIES,
    }


def is_configured():
    return bool(SIBERIAN_ENABLED and SIBERIAN_BASE_URL and (SIBERIAN_API_KEY or SIBERIAN_API_TOKEN))


def config_issues():
    issues = []
    if not SIBERIAN_ENABLED:
        issues.append("SIBERIAN_ENABLED=false — connector disabled")
    if not SIBERIAN_BASE_URL:
        issues.append("SIBERIAN_API_BASE_URL not configured")
    if not (SIBERIAN_API_KEY or SIBERIAN_API_TOKEN):
        issues.append("No auth configured (SIBERIAN_API_KEY or SIBERIAN_API_TOKEN required)")
    return issues


def build_auth_headers():
    headers = {"Accept": "application/json"}
    if SIBERIAN_API_KEY:
        headers["X-API-Key"] = SIBERIAN_API_KEY
    if SIBERIAN_API_TOKEN:
        headers["Authorization"] = f"Bearer {SIBERIAN_API_TOKEN}"
    return headers


def safe_get(path, params=None, retries=0):
    """
    Execute a read-only GET request to Sistema Siberian API.
    Blocks: POST, PUT, PATCH, DELETE.
    Returns structured result with source and validation_status.
    """
    if not is_configured():
        issues = config_issues()
        return {
            "success": False,
            "status": "not_configured" if not SIBERIAN_ENABLED else "misconfigured",
            "data": None,
            "source": "pending_api",
            "mode": "read_only",
            "errors": issues,
            "_token_exposed": False,
        }

    url = f"{SIBERIAN_BASE_URL}{path}"

    try:
        headers = build_auth_headers()
        req = urllib.request.Request(url, headers=headers, method="GET")
        resp = urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)
        raw = resp.read().decode("utf-8")

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {
                "success": False,
                "status": "invalid_response",
                "data": None,
                "source": "sistema_siberian_api",
                "mode": "read_only",
                "errors": ["Response was not valid JSON"],
                "_token_exposed": False,
            }

        return {
            "success": True,
            "status": "online",
            "data": data,
            "source": "sistema_siberian_api",
            "mode": "read_only",
            "validation_status": "pending_validation",
            "received_at": datetime.now(timezone.utc).isoformat(),
            "warnings": [],
            "_token_exposed": False,
        }

    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            return {
                "success": False,
                "status": "auth_error",
                "data": None,
                "source": "sistema_siberian_api",
                "mode": "read_only",
                "errors": ["Authentication failed. Check SIBERIAN_API_KEY or SIBERIAN_API_TOKEN."],
                "_token_exposed": False,
            }
        if e.code == 404:
            return {
                "success": False,
                "status": "endpoint_not_found",
                "data": None,
                "source": "sistema_siberian_api",
                "mode": "read_only",
                "errors": [f"Endpoint not found: {path}"],
                "_token_exposed": False,
            }
        return {
            "success": False,
            "status": f"http_error_{e.code}",
            "data": None,
            "source": "sistema_siberian_api",
            "mode": "read_only",
            "errors": [f"HTTP {e.code}: {e.reason}"],
            "_token_exposed": False,
        }

    except urllib.error.URLError as e:
        if retries < MAX_RETRIES:
            return safe_get(path, params, retries + 1)
        return {
            "success": False,
            "status": "timeout" if "timed out" in str(e).lower() else "connection_error",
            "data": None,
            "source": "sistema_siberian_api",
            "mode": "read_only",
            "errors": [str(e)],
            "_token_exposed": False,
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "data": None,
            "source": "sistema_siberian_api",
            "mode": "read_only",
            "errors": [str(e)],
            "_token_exposed": False,
        }


def get_health():
    return safe_get("/api/health")


def get_companies():
    return safe_get("/api/companies")


def get_stores():
    return safe_get("/api/stores")


def get_sales_summary():
    return safe_get("/api/sales/summary")


def get_finance_summary():
    return safe_get("/api/finance/summary")


def get_products_summary():
    return safe_get("/api/products/summary")


def get_stock_summary():
    return safe_get("/api/stock/summary")
