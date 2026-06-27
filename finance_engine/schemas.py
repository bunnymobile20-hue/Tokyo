from pydantic import BaseModel
from typing import Optional, List, Any

class FinanceEngineResponse(BaseModel):
    origin: str = "tokyo_finance_engine"
    data_status: str
    confidence: str
    safe_to_display: bool
    data: Optional[Any] = None
    warnings: List[str] = []
    missing_fields: List[str] = []

def build_finance_error(gate_response) -> FinanceEngineResponse:
    return FinanceEngineResponse(
        data_status=gate_response.data_status,
        confidence=gate_response.confidence,
        safe_to_display=False,
        warnings=gate_response.warnings,
        missing_fields=gate_response.missing_fields
    )
