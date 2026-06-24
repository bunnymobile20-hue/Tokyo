from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class HermesCommandRequest(BaseModel):
    source: str = "tokyoos"
    request_id: str
    command: str
    mode: str = "dry_run"
    risk: str = "low"
    requires_confirmation: bool = False
    llm_provider: str = "ollama"
    ollama_model: str = "qwen2.5:32b"
    context: Dict[str, Any] = {}

class HermesExecuteRequest(BaseModel):
    command: str
    mode: str = "active_assisted"
    source: str = "tokyoos"
    llm_provider: str = "ollama"
    model: str = "qwen2.5:32b"

class HermesConfirmRequest(BaseModel):
    pending_id: str
    confirm: bool
    human_confirmation: str = "CONFIRM_HERMES_ACTION"

class HermesCommandResponse(BaseModel):
    ok: bool
    job_id: Optional[str] = None
    status: str
    summary: str
    actions_planned: List[Dict[str, Any]] = []
    actions_executed: List[Dict[str, Any]] = []
    requires_confirmation: bool = False
    risk: str = "low"
    logs_sanitized: List[str] = []
    error: Optional[str] = None

class AutomationJob(BaseModel):
    job_id: str
    command: str
    status: str
    risk: str
    mode: str
    created_at: str
    executed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
