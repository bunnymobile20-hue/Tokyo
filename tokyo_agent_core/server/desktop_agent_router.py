import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/tokyo/desktop-agent", tags=["desktop-agent"])
operator_router = APIRouter(prefix="/tokyo/desktop-agent-operator", tags=["desktop-agent-operator"])

# --- Models ---
class RegisterRequest(BaseModel):
    workspace: str
    capabilities: Dict[str, Any]

class HeartbeatRequest(BaseModel):
    status: str

class TaskResultRequest(BaseModel):
    task_id: str
    success: bool
    result: Dict[str, Any]
    logs: List[str]

class ExecuteRequest(BaseModel):
    command: str
    action_type: str = "generic"
    payload: Dict[str, Any] = {}

class AgentStatusResponse(BaseModel):
    online: bool
    last_heartbeat: Optional[datetime] = None
    workspace: Optional[str] = None
    capabilities: Dict[str, Any] = {}
    pending_tasks_count: int = 0
    completed_tasks_count: int = 0

# --- In-Memory State ---
class DesktopAgentState:
    def __init__(self):
        self.last_heartbeat: Optional[datetime] = None
        self.workspace: Optional[str] = None
        self.capabilities: Dict[str, Any] = {}
        self.ip_address: Optional[str] = None
        
        self.pending_tasks: List[Dict[str, Any]] = []
        self.running_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []

    def is_online(self) -> bool:
        if not self.last_heartbeat:
            return False
        diff = (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds()
        return diff < 60  # 1 minute timeout

agent_state = DesktopAgentState()

# --- Agent Facing Routes ---

@router.post("/register")
async def register_agent(req: RegisterRequest, request: Request):
    agent_state.workspace = req.workspace
    agent_state.capabilities = req.capabilities
    agent_state.last_heartbeat = datetime.now(timezone.utc)
    agent_state.ip_address = request.client.host if request.client else "unknown"
    return {"status": "registered"}

@router.post("/heartbeat")
async def agent_heartbeat(req: HeartbeatRequest):
    agent_state.last_heartbeat = datetime.now(timezone.utc)
    return {"status": "ok"}

@router.get("/tasks/next")
async def get_next_task():
    if not agent_state.pending_tasks:
        return {"has_task": False}
    
    task = agent_state.pending_tasks.pop(0)
    task["status"] = "running"
    task["updated_at"] = datetime.now(timezone.utc).isoformat()
    agent_state.running_tasks[task["task_id"]] = task
    
    return {
        "has_task": True,
        "task": task
    }

@router.post("/tasks/result")
async def submit_task_result(req: TaskResultRequest):
    if req.task_id not in agent_state.running_tasks:
        raise HTTPException(status_code=404, detail="Task not found or not running")
    
    task = agent_state.running_tasks.pop(req.task_id)
    task["status"] = "completed" if req.success else "failed"
    task["result"] = req.result
    task["logs"] = req.logs
    task["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    agent_state.completed_tasks.insert(0, task)
    # Keep only last 50
    agent_state.completed_tasks = agent_state.completed_tasks[:50]
    
    return {"status": "accepted"}

# --- Operator/UI Facing Routes ---

@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    return AgentStatusResponse(
        online=agent_state.is_online(),
        last_heartbeat=agent_state.last_heartbeat,
        workspace=agent_state.workspace,
        capabilities=agent_state.capabilities,
        pending_tasks_count=len(agent_state.pending_tasks),
        completed_tasks_count=len(agent_state.completed_tasks)
    )

@router.get("/tasks")
async def list_recent_tasks():
    return {
        "pending": agent_state.pending_tasks,
        "running": list(agent_state.running_tasks.values()),
        "completed": agent_state.completed_tasks
    }

@operator_router.post("/execute")
async def enqueue_task(req: ExecuteRequest):
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "command": req.command,
        "action_type": req.action_type,
        "payload": req.payload,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    agent_state.pending_tasks.append(task)
    return {"status": "enqueued", "task_id": task_id}
