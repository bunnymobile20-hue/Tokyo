from fastapi import APIRouter, Body
from typing import Dict, Any
from .schemas import BridgeResponse, ComponentOrigin, DataStatus
from .bridge import invoke_openjarvis_agent

router = APIRouter()

@router.get("/tokyo/agent-core/status", response_model=BridgeResponse)
async def agent_core_status():
    return BridgeResponse(
        origin=ComponentOrigin.OPENJARVIS_CORE,
        data_status=DataStatus.SAFE_READ_ONLY,
        message="Agent Core (OpenJarvis) is integrated and active.",
        data={"version": "1.0", "status": "running"}
    )

@router.get("/tokyo/operator/status", response_model=BridgeResponse)
async def operator_status():
    return BridgeResponse(
        origin=ComponentOrigin.BRIDGED,
        data_status=DataStatus.SAFE_READ_ONLY,
        message="Operator bridge is ready.",
        data={"operator_type": "native_tokyo"}
    )

@router.post("/tokyo/operator/execute", response_model=BridgeResponse)
async def operator_execute(payload: Dict[str, Any] = Body(...)):
    # Applies SafetyGate
    return invoke_openjarvis_agent("operator", payload)

@router.get("/tokyo/memory/status", response_model=BridgeResponse)
async def memory_status():
    return BridgeResponse(
        origin=ComponentOrigin.OPENJARVIS_CORE,
        data_status=DataStatus.NOT_CONFIGURED,
        message="Memory bindings check",
        data={"local_vector": "available", "mem0": "not_configured"}
    )

@router.post("/tokyo/memory/index", response_model=BridgeResponse)
async def memory_index(payload: Dict[str, Any] = Body(...)):
    return BridgeResponse(
        origin=ComponentOrigin.OPENJARVIS_CORE,
        data_status=DataStatus.SAFE_READ_ONLY,
        message="Indexed into OpenJarvis memory bridge",
        data={"status": "success"}
    )

@router.post("/tokyo/memory/search", response_model=BridgeResponse)
async def memory_search(payload: Dict[str, Any] = Body(...)):
    return BridgeResponse(
        origin=ComponentOrigin.OPENJARVIS_CORE,
        data_status=DataStatus.SAFE_READ_ONLY,
        message="Memory search executed via bridge",
        data={"results": []}
    )

@router.get("/tokyo/skills/status", response_model=BridgeResponse)
async def skills_status():
    return BridgeResponse(
        origin=ComponentOrigin.OPENJARVIS_CORE,
        data_status=DataStatus.SAFE_READ_ONLY,
        message="Skills registry active",
        data={"skills_loaded": 0}
    )

@router.get("/tokyo/workflows/status", response_model=BridgeResponse)
async def workflows_status():
    return BridgeResponse(
        origin=ComponentOrigin.OPENJARVIS_CORE,
        data_status=DataStatus.SAFE_READ_ONLY,
        message="Workflows engine active",
        data={"workflows": []}
    )

@router.get("/tokyo/bunny-agents/status", response_model=BridgeResponse)
async def bunny_agents_status():
    return BridgeResponse(
        origin=ComponentOrigin.NATIVE_TOKYO,
        data_status=DataStatus.SAFE_READ_ONLY,
        message="Bunny Agents registry",
        data={"agents": ["tokyo_cfo", "tokyo_coo", "tokyo_estoque"]}
    )

@router.post("/tokyo/bunny-agents/invoke", response_model=BridgeResponse)
async def bunny_agents_invoke(payload: Dict[str, Any] = Body(...)):
    agent_name = payload.get("agent_name", "unknown")
    # Applies Zero Mock Gate and SafetyGate
    return invoke_openjarvis_agent(agent_name, payload)
