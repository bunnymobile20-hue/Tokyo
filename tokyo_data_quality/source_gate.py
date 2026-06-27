from .schemas import DataQualityGateResponse, build_gate_error
from .warnings import check_missing_fields, generate_warnings
from .confidence import calculate_confidence
from typing import List

def require_real_data(siberian_response: dict, required_fields: List[str] = None) -> DataQualityGateResponse:
    if not isinstance(siberian_response, dict):
        return build_gate_error("DATA_SOURCE_NOT_REAL")
        
    data_status = siberian_response.get("data_status")
    
    if data_status == "SIBERIAN_NOT_CONFIGURED":
        return build_gate_error("SIBERIAN_NOT_CONFIGURED")
        
    if data_status != "real_data":
        return build_gate_error("DATA_SOURCE_NOT_REAL")
        
    # Extrai o payload real (geralmente em "data")
    payload = siberian_response.get("data", {})
    
    missing_fields = []
    total_fields = len(required_fields) if required_fields else 0
    if required_fields:
        missing_fields = check_missing_fields(payload, required_fields)
        
    confidence = calculate_confidence(len(missing_fields), total_fields)
    warnings = generate_warnings(missing_fields)
    
    # Block if too many missing fields for calculation
    if confidence == "low" and total_fields > 0:
        return build_gate_error("insufficient_real_data")
        
    return DataQualityGateResponse(
        safe=True,
        data_status="real_data",
        confidence=confidence,
        warnings=warnings,
        missing_fields=missing_fields,
        real_data_payload=payload
    )
