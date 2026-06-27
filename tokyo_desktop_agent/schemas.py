from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class TaskMessage(BaseModel):
    task_id: str
    command: str
    action_type: str
    payload: Dict[str, Any]

class TaskResult(BaseModel):
    task_id: str
    success: bool
    result: Dict[str, Any]
    logs: List[str]
