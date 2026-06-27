from .schemas import FinanceEngineResponse

def calculate_margins(dre_response: FinanceEngineResponse) -> FinanceEngineResponse:
    if not dre_response.safe_to_display:
        return dre_response
        
    dre = dre_response.data
    net_revenue = dre.get("receita_liquida", 0)
    net_profit = dre.get("lucro_liquido", 0)
    
    if net_revenue == 0:
        margin = 0
    else:
        margin = (net_profit / net_revenue) * 100
        
    dre["margem_liquida_pct"] = round(margin, 2)
    
    return FinanceEngineResponse(
        data_status="real_data",
        confidence=dre_response.confidence,
        safe_to_display=True,
        data=dre,
        warnings=dre_response.warnings
    )
