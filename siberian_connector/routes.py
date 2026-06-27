from fastapi import APIRouter
from .config import settings
from .schemas import not_configured_response, build_response
from .health import check_health
from .discovery import discover_endpoints
from .client import siberian_client
from .cache import save_cache, load_cache
from .policy import SiberianPolicyError

router = APIRouter(prefix="/tokyo/siberian", tags=["Siberian Connector"])

def get_data_or_mock(endpoint: str):
    if not settings.is_configured:
        return not_configured_response(endpoint)
    # Tenta carregar do cache primeiro (Read-Only approach)
    cached = load_cache(endpoint)
    if cached:
        return build_response("real_data", safe_to_display=True, data=cached, endpoint=endpoint)
        
    return build_response("real_data_pending", safe_to_display=True, data={}, endpoint=endpoint)

@router.get("/status")
async def get_status():
    status_data = settings.safe_status()
    ds = "SIBERIAN_CONFIGURED" if settings.is_configured else "SIBERIAN_NOT_CONFIGURED"
    return build_response(ds, True, data=status_data, endpoint="status")

@router.get("/health")
async def health():
    return build_response("health_check", True, data=check_health(), endpoint="health")

@router.get("/discovery")
async def discovery():
    return await discover_endpoints()

@router.get("/companies")
async def get_companies():
    return get_data_or_mock("companies")

@router.get("/stores")
async def get_stores():
    return get_data_or_mock("stores")

@router.get("/products")
async def get_products():
    return get_data_or_mock("products")

@router.get("/sales")
async def get_sales():
    return get_data_or_mock("sales")

@router.get("/stock")
async def get_stock():
    return get_data_or_mock("stock")

@router.get("/finance")
async def get_finance():
    return get_data_or_mock("finance")

@router.get("/reports")
async def get_reports():
    return get_data_or_mock("reports")

@router.post("/cache/refresh-readonly")
async def refresh_cache_readonly():
    # Isso é apenas para a TokyoOS renovar o cache efetuando GETs permitidos no ERP
    if not settings.is_configured:
        return not_configured_response("cache_refresh")
        
    # Exemplo: Atualizar empresas
    try:
        data = await siberian_client.request("GET", "api/companies")
        save_cache("companies", data)
        return build_response("cache_updated", True, data={"status": "success"}, endpoint="cache_refresh")
    except SiberianPolicyError as e:
        return build_response("blocked", True, data={"error": str(e)}, endpoint="cache_refresh")
    except Exception as e:
        if str(e) == "SIBERIAN_NOT_CONFIGURED":
            return not_configured_response("cache_refresh")
        return build_response("error", True, data={"error": str(e)}, endpoint="cache_refresh")
