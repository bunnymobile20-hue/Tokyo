from typing import Any, Dict
from .schemas import BridgeResponse, ComponentOrigin, DataStatus
from .adapters import apply_zero_mock_gate, validate_safety_gate

def invoke_openjarvis_agent(agent_name: str, payload: Dict[str, Any]) -> BridgeResponse:
    action = payload.get("action", "")
    
    if not validate_safety_gate(action):
        return BridgeResponse(
            origin=ComponentOrigin.NATIVE_TOKYO,
            data_status=DataStatus.BLOCKED,
            message="Action blocked by SafetyGate",
            data={"reason": "Prohibited command or path detected"}
        )

    # All business agents must pass through zero mock gate
    if agent_name in ["tokyo_cfo", "tokyo_coo", "tokyo_estoque"]:
        return apply_zero_mock_gate(agent_name, payload)

    return BridgeResponse(
        origin=ComponentOrigin.OPENJARVIS_CORE,
        data_status=DataStatus.SAFE_READ_ONLY,
        message=f"Agent {agent_name} invoked successfully via OpenJarvis Core.",
        data={"result": "success", "action": action}
    )
