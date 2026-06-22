"""
Siberian Connector API routes for TokyoOS FastAPI app.
Import these in app.py to register all Siberian endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from . import service

router = APIRouter(prefix="/tokyo/siberian", tags=["siberian"])


def _safe(data):
    """Wrap response with _meta block"""
    data["_meta"] = {
        "token_exposed": False,
        "mode": "read_only",
        "external_write_enabled": False,
    }
    return JSONResponse(content=data)


@router.get("/status")
async def siberian_status():
    return _safe(service.get_status())


@router.get("/health")
async def siberian_health():
    return _safe(service.check_health())


@router.get("/schema")
async def siberian_schema():
    return _safe(service.get_schema())


@router.get("/capabilities")
async def siberian_capabilities():
    return _safe(service.get_schema())


@router.get("/companies")
async def siberian_companies():
    return _safe(service.fetch_companies())


@router.get("/stores")
async def siberian_stores():
    return _safe(service.fetch_stores())


@router.get("/sales/summary")
async def siberian_sales_summary():
    return _safe(service.fetch_sales_summary())


@router.get("/finance/summary")
async def siberian_finance_summary():
    return _safe(service.fetch_finance_summary())


@router.get("/products/summary")
async def siberian_products_summary():
    return _safe(service.fetch_products_summary())


@router.get("/stock/summary")
async def siberian_stock_summary():
    return _safe(service.fetch_stock_summary())


@router.get("/real-api-readiness")
async def siberian_real_api_readiness():
    return _safe(service.get_real_api_readiness())
