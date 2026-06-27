from fastapi import APIRouter
from .schemas import BridgeResponse, ComponentOrigin, DataStatus

router = APIRouter()

@router.get("/status", response_model=BridgeResponse)
async def get_bridge_status():
    return BridgeResponse(
        origin=ComponentOrigin.BRIDGED,
        data_status=DataStatus.MOCK_ACTIVE,
        message="Bridge is healthy",
        data={
            "agent_core_status": "openjarvis_core_ready",
            "safety_gate": "active"
        }
    )
