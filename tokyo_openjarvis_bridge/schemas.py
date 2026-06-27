from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class ComponentOrigin(str, Enum):
    NATIVE_TOKYO = "native_tokyo"
    OPENJARVIS_CORE = "openjarvis_core"
    BRIDGED = "bridged"

class DataStatus(str, Enum):
    MOCK_ACTIVE = "mock_active"
    NOT_CONFIGURED = "not_configured"
    SAFE_READ_ONLY = "safe_read_only"
    BLOCKED = "blocked"
    DATA_SOURCE_NOT_REAL = "DATA_SOURCE_NOT_REAL"
    SIBERIAN_NOT_CONFIGURED = "SIBERIAN_NOT_CONFIGURED"

class BridgeResponse(BaseModel):
    origin: ComponentOrigin
    data_status: DataStatus
    message: str
    data: Optional[Dict[str, Any]] = None
