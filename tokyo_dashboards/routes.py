from fastapi import APIRouter
from tokyo_data_quality import require_real_data, build_gate_error
from finance_engine.siberian_mapper import map_sales_data, map_stock_data
from finance_engine.dre_builder import build_dre
from finance_engine.kpi_calculator import calculate_margins
from siberian_connector.config import settings
from siberian_connector.cache import load_cache
from datetime import datetime

router = APIRouter(prefix="/tokyo/dashboard", tags=["Dashboards"])

def get_base_response(gate_res):
    return {
        "origin": "tokyo_dashboard",
        "source": "siberian",
        "data_status": gate_res.data_status if hasattr(gate_res, "data_status") else gate_res.get("data_status"),
        "confidence": getattr(gate_res, "confidence", "none"),
        "safe_to_display": getattr(gate_res, "safe_to_display", False) or getattr(gate_res, "safe", False),
        "write_enabled": False,
        "last_sync": datetime.utcnow().isoformat() + "Z",
        "warnings": getattr(gate_res, "warnings", []),
        "missing_fields": getattr(gate_res, "missing_fields", []),
        "data": getattr(gate_res, "data", None) or getattr(gate_res, "real_data_payload", None)
    }

# Finance
@router.get("/finance/status")
async def finance_status():
    if not settings.is_configured:
        return get_base_response(build_gate_error("SIBERIAN_NOT_CONFIGURED"))
    return get_base_response(build_gate_error("real_data_pending"))

@router.get("/finance/summary")
async def finance_summary():
    if not settings.is_configured:
        return get_base_response(build_gate_error("SIBERIAN_NOT_CONFIGURED"))
    
    # Simula chamada interna pro siberian via cache
    sales = load_cache("sales") or {"data_status": "SIBERIAN_NOT_CONFIGURED"}
    mapped = map_sales_data(sales)
    return get_base_response(mapped)

@router.get("/finance/dre")
async def finance_dre():
    if not settings.is_configured:
        return get_base_response(build_gate_error("SIBERIAN_NOT_CONFIGURED"))
        
    sales = load_cache("sales") or {"data_status": "SIBERIAN_NOT_CONFIGURED"}
    finance = load_cache("finance") or {"data_status": "SIBERIAN_NOT_CONFIGURED"}
    
    dre = build_dre(sales, finance)
    dre_with_kpi = calculate_margins(dre)
    return get_base_response(dre_with_kpi)

# Stock
@router.get("/stock/status")
async def stock_status():
    if not settings.is_configured:
        return get_base_response(build_gate_error("SIBERIAN_NOT_CONFIGURED"))
    return get_base_response(build_gate_error("real_data_pending"))

@router.get("/stock/summary")
async def stock_summary():
    if not settings.is_configured:
        return get_base_response(build_gate_error("SIBERIAN_NOT_CONFIGURED"))
        
    stock = load_cache("stock") or {"data_status": "SIBERIAN_NOT_CONFIGURED"}
    mapped = map_stock_data(stock)
    return get_base_response(mapped)

# Executive
@router.get("/executive/status")
async def executive_status():
    if not settings.is_configured:
        return get_base_response(build_gate_error("SIBERIAN_NOT_CONFIGURED"))
    return get_base_response(build_gate_error("real_data_pending"))

@router.get("/executive/summary")
async def executive_summary():
    if not settings.is_configured:
        return get_base_response(build_gate_error("SIBERIAN_NOT_CONFIGURED"))
        
    # Scaffold for executive summary relying on finance and stock
    dre = await finance_dre()
    stock = await stock_summary()
    
    if not dre["safe_to_display"] or not stock["safe_to_display"]:
        return get_base_response(build_gate_error("insufficient_real_data"))
        
    exec_data = {
        "overall_health": "stable",
        "finance": dre["data"],
        "stock": stock["data"]
    }
    
    class FakeRes:
        pass
    fake = FakeRes()
    fake.data_status = "real_data"
    fake.confidence = "medium"
    fake.safe_to_display = True
    fake.warnings = dre["warnings"] + stock["warnings"]
    fake.missing_fields = dre["missing_fields"] + stock["missing_fields"]
    fake.data = exec_data
    
    return get_base_response(fake)
