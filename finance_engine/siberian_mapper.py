from tokyo_data_quality import require_real_data
from .schemas import FinanceEngineResponse, build_finance_error

def map_sales_data(siberian_response: dict) -> FinanceEngineResponse:
    gate = require_real_data(siberian_response, required_fields=["total_vendas"])
    
    if not gate.safe:
        return build_finance_error(gate)
        
    payload = gate.real_data_payload
    # Map raw Siberian format to Tokyo Finance Engine format
    mapped_data = {
        "gross_revenue": payload.get("total_vendas", 0),
        "discounts": payload.get("descontos", 0),
        "net_revenue": payload.get("total_vendas", 0) - payload.get("descontos", 0)
    }
    
    return FinanceEngineResponse(
        data_status="real_data",
        confidence=gate.confidence,
        safe_to_display=True,
        data=mapped_data,
        warnings=gate.warnings,
        missing_fields=gate.missing_fields
    )

def map_stock_data(siberian_response: dict) -> FinanceEngineResponse:
    gate = require_real_data(siberian_response)
    
    if not gate.safe:
        return build_finance_error(gate)
        
    payload = gate.real_data_payload
    
    # Exemplo: Array de produtos vindo do ERP
    items = payload if isinstance(payload, list) else payload.get("items", [])
    
    total_items = len(items)
    zero_stock = sum(1 for item in items if item.get("quantidade", 0) <= 0)
    
    mapped_data = {
        "total_products": total_items,
        "zero_stock_products": zero_stock,
        "raw_items": items
    }
    
    return FinanceEngineResponse(
        data_status="real_data",
        confidence=gate.confidence,
        safe_to_display=True,
        data=mapped_data,
        warnings=gate.warnings,
        missing_fields=gate.missing_fields
    )
