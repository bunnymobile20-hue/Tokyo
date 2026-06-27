from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class TransparentResponse(BaseModel):
    origin: str = "tokyoos"
    source: str = "siberian"
    mode: str = "read_only"
    write_enabled: bool = False
    data_status: str
    safe_to_display: bool
    endpoint: Optional[str] = None
    timestamp: Optional[str] = None
    data: Optional[Any] = None

def build_response(data_status: str, safe_to_display: bool, data: Any = None, endpoint: str = None) -> TransparentResponse:
    from datetime import datetime
    return TransparentResponse(
        data_status=data_status,
        safe_to_display=safe_to_display,
        data=data,
        endpoint=endpoint,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

def not_configured_response(endpoint: str = None) -> TransparentResponse:
    return build_response(
        data_status="SIBERIAN_NOT_CONFIGURED",
        safe_to_display=False,
        endpoint=endpoint
    )
