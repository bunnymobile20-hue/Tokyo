from pydantic import BaseModel
from typing import Optional, List, Any

class DataQualityGateResponse(BaseModel):
    safe: bool
    data_status: str
    confidence: str
    warnings: List[str]
    missing_fields: List[str]
    real_data_payload: Optional[Any] = None

def build_gate_error(reason: str) -> DataQualityGateResponse:
    return DataQualityGateResponse(
        safe=False,
        data_status=reason,
        confidence="none",
        warnings=[f"Blocked by Data Gate: {reason}"],
        missing_fields=[],
        real_data_payload=None
    )
