from typing import Any, Dict
from .schemas import BridgeResponse, ComponentOrigin, DataStatus
import os

def apply_zero_mock_gate(agent_name: str, requested_data: Dict[str, Any]) -> BridgeResponse:
    siberian_connected = os.getenv("SIBERIAN_CONNECTED", "false").lower() == "true"

    if not siberian_connected:
        return BridgeResponse(
            origin=ComponentOrigin.BRIDGED,
            data_status=DataStatus.SIBERIAN_NOT_CONFIGURED,
            message=f"[{agent_name}] MOCK DATA ACTIVE - Siberian ERP disconnected.",
            data={"warning": "DATA_SOURCE_NOT_REAL"}
        )
    
    return BridgeResponse(
        origin=ComponentOrigin.BRIDGED,
        data_status=DataStatus.SAFE_READ_ONLY,
        message=f"[{agent_name}] Data accessed via Siberian Connector.",
        data=requested_data
    )

def validate_safety_gate(action: str) -> bool:
    blocked_actions = ["rm -rf", "sudo", "shutdown", "reboot", "pkill", "killall", "/etc/passwd", ".env"]
    for blocked in blocked_actions:
        if blocked in action.lower():
            return False
    return True
