"""FastAPI routes for TokyoOS Agent Core (absorb OpenJarvis backend features)."""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from openjarvis import Jarvis
from openjarvis.core.registry import AgentRegistry, ToolRegistry
from openjarvis.skills.manager import SkillManager
from openjarvis.core.events import EventBus

router = APIRouter(prefix="/tokyo/agent-core", tags=["Agent Core"])

class AskRequest(BaseModel):
    query: str
    agent: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None

class MemorySearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class MemoryIndexRequest(BaseModel):
    path: str
    chunk_size: Optional[int] = 512
    chunk_overlap: Optional[int] = 64

# Singleton Jarvis instance
_jarvis_instance = None

def get_jarvis() -> Jarvis:
    global _jarvis_instance
    if _jarvis_instance is None:
        _jarvis_instance = Jarvis()
    return _jarvis_instance

@router.get("/status")
async def get_status(j: Jarvis = Depends(get_jarvis)):
    cfg = j.config
    try:
        from tokyo_agent_core._rust_bridge import RUST_AVAILABLE
    except ImportError:
        RUST_AVAILABLE = False
        
    return {
        "status": "active",
        "version": j.version,
        "default_engine": cfg.intelligence.preferred_engine or "ollama",
        "default_model": cfg.intelligence.default_model or "qwen2.5:32b-instruct",
        "memory_backend": cfg.memory.default_backend,
        "telemetry_enabled": cfg.telemetry.enabled,
        "rust_bridge_active": RUST_AVAILABLE
    }

@router.get("/agents")
async def list_agents():
    # Import agent modules to ensure they are registered
    import openjarvis.agents
    agents = []
    for key in AgentRegistry.keys():
        cls = AgentRegistry.get(key)
        agents.append({
            "id": key,
            "name": cls.__name__,
            "description": cls.__doc__.strip() if cls.__doc__ else "Sem descrição.",
            "accepts_tools": getattr(cls, "accepts_tools", False)
        })
    return {"agents": agents}

@router.get("/skills")
async def list_skills():
    bus = EventBus()
    manager = SkillManager(bus)
    skills_path = Path(__file__).parent / "skills" / "data"
    if skills_path.exists():
        manager.discover([skills_path])
        
    skills_list = []
    for name in manager.skill_names():
        manifest = manager.resolve(name)
        skills_list.append({
            "name": manifest.name,
            "description": manifest.description,
            "version": manifest.version,
            "author": manifest.author or "TokyoOS Core",
            "requirements": manifest.required_capabilities,
            "entrypoint": manifest.steps[0].tool_name if manifest.steps else "None"
        })
    return {"skills": skills_list}

@router.get("/tools")
async def list_tools():
    import openjarvis.tools
    tools_list = []
    for key in ToolRegistry.keys():
        try:
            cls = ToolRegistry.get(key)
            tool = cls()
            spec = tool.spec
            tools_list.append({
                "id": key,
                "name": spec.name,
                "description": spec.description,
                "parameters": spec.parameters,
                "category": spec.category,
                "requires_confirmation": spec.requires_confirmation
            })
        except Exception:
            tools_list.append({
                "id": key,
                "name": key,
                "description": f"Ferramenta OpenJarvis registrada: {key}",
                "parameters": {},
                "category": "general",
                "requires_confirmation": False
            })
    return {"tools": tools_list}

@router.get("/memory/stats")
async def get_memory_stats(j: Jarvis = Depends(get_jarvis)):
    try:
        return j.memory.stats()
    except Exception as e:
        return {"backend": j.config.memory.default_backend, "count": 0, "error": str(e)}

@router.post("/memory/search")
async def memory_search(req: MemorySearchRequest, j: Jarvis = Depends(get_jarvis)):
    try:
        results = j.memory.search(req.query, top_k=req.top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/index")
async def memory_index(req: MemoryIndexRequest, j: Jarvis = Depends(get_jarvis)):
    path = Path(req.path)
    if not path.is_absolute():
        workspace_dir = Path(os.getenv("TOKYO_DATA_DIR", "/data/tokyo")) / "workspace"
        path = (workspace_dir / req.path).resolve()
        
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Caminho não encontrado: {req.path}")
        
    try:
        res = j.memory.index(str(path), chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_agent(req: AskRequest, j: Jarvis = Depends(get_jarvis)):
    try:
        response = j.ask(
            req.query,
            agent=req.agent,
            model=req.model,
            temperature=req.temperature
        )
        return {
            "response": response,
            "agent": req.agent,
            "model": req.model or j.config.intelligence.default_model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows")
async def list_workflows():
    return {
        "workflows": [
            {
                "id": "morning_briefing",
                "name": "Briefing Matinal Bunny Dreams",
                "description": "Coleta dados financeiros do Siberian ERP, verifica estoque e gera resumo operacional.",
                "steps": ["coleta_dados", "analise_cfo", "alerta_estoque", "consolidacao"]
            }
        ]
    }
