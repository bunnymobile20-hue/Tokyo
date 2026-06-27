from .siberian_mapper import map_sales_data
from .schemas import FinanceEngineResponse, build_finance_error
from tokyo_data_quality import require_real_data

def build_dre(siberian_sales_response: dict, siberian_finance_response: dict) -> FinanceEngineResponse:
    # 1. Valida Vendas
    sales_mapper = map_sales_data(siberian_sales_response)
    if not sales_mapper.safe_to_display:
        return sales_mapper
        
    # 2. Valida Despesas (Financeiro)
    finance_gate = require_real_data(siberian_finance_response, required_fields=["despesas_operacionais"])
    if not finance_gate.safe:
        return build_finance_error(finance_gate)
        
    # Construção DRE
    net_revenue = sales_mapper.data.get("net_revenue", 0)
    opex = finance_gate.real_data_payload.get("despesas_operacionais", 0)
    
    dre_data = {
        "receita_liquida": net_revenue,
        "despesas_operacionais": opex,
        "lucro_operacional": net_revenue - opex,
        "lucro_liquido": net_revenue - opex # simplificado para o scaffold
    }
    
    confidence = "high" if sales_mapper.confidence == "high" and finance_gate.confidence == "high" else "medium"
    
    return FinanceEngineResponse(
        data_status="real_data",
        confidence=confidence,
        safe_to_display=True,
        data=dre_data,
        warnings=sales_mapper.warnings + finance_gate.warnings
    )
