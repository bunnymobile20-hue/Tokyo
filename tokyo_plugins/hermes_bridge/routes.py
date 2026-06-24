from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Dict, Any, List
import uuid
from .schemas import HermesCommandRequest, HermesCommandResponse, HermesExecuteRequest, HermesConfirmRequest
from .service import HermesService

router = APIRouter(prefix="/tokyo/plugins/hermes", tags=["hermes_plugin"])

# Global instance for in-memory pending jobs state across requests
_hermes_service = HermesService()

def get_hermes_service():
    return _hermes_service

@router.get("/status")
async def get_status(service: HermesService = Depends(get_hermes_service)):
    return service.get_status()

@router.get("/capabilities")
async def get_capabilities(service: HermesService = Depends(get_hermes_service)):
    return service.get_capabilities()

@router.post("/test-connection")
async def test_connection(service: HermesService = Depends(get_hermes_service)):
    status = service.get_status()
    if "connected" in status["status"] or "fallback_adapter_ready" in status["status"]:
        return {"ok": True, "message": "Connection to Hermes / Adapter successful"}
    raise HTTPException(status_code=503, detail="Hermes is offline or not configured")

@router.get("/ollama/status")
async def get_ollama_status(service: HermesService = Depends(get_hermes_service)):
    return service.get_ollama_status()

@router.post("/execute", response_model=HermesCommandResponse)
async def execute_real_command(request: HermesExecuteRequest, service: HermesService = Depends(get_hermes_service)):
    return service.execute_command(request)

@router.post("/confirm", response_model=HermesCommandResponse)
async def confirm_command(request: HermesConfirmRequest, service: HermesService = Depends(get_hermes_service)):
    return service.confirm_action(request)

@router.post("/dry-run", response_model=HermesCommandResponse)
async def execute_dry_run(request: HermesCommandRequest, service: HermesService = Depends(get_hermes_service)):
    request.mode = "dry_run"
    return service.process_command(request)

@router.post("/command", response_model=HermesCommandResponse)
async def execute_command(request: HermesCommandRequest, service: HermesService = Depends(get_hermes_service)):
    return service.process_command(request)

@router.get("/audit")
async def get_audit_logs():
    # Placeholder for actual DB query
    return {
        "logs": [
            {"id": str(uuid.uuid4()), "action": "test_connection", "risk": "low", "status": "completed"}
        ]
    }

# --- LAB ENDPOINTS ---

# --- BROWSER ENDPOINTS ---
from .browser_provider import detect_browser_provider, browser_health, open_url, extract_title, extract_text, summarize_url

@router.get("/browser/status")
async def get_browser_status():
    return browser_health()

from pydantic import BaseModel
class UrlRequest(BaseModel):
    url: str

@router.post("/browser/open-url")
async def browser_open_url(req: UrlRequest):
    return open_url(req.url)

@router.post("/browser/extract")
async def browser_extract(req: UrlRequest):
    return extract_text(req.url)

@router.post("/browser/summarize-url")
async def browser_summarize(req: UrlRequest):
    return summarize_url(req.url)

# --- FIRECRAWL ENDPOINTS ---
from .firecrawl_provider import detect_firecrawl, firecrawl_health, scrape_url, crawl_url, summarize_crawl

@router.get("/firecrawl/status")
async def get_firecrawl_status():
    return firecrawl_health()

@router.post("/firecrawl/scrape")
async def firecrawl_scrape(req: UrlRequest):
    return scrape_url(req.url)

@router.post("/firecrawl/crawl")
async def firecrawl_crawl_route(req: UrlRequest):
    return crawl_url(req.url)

# --- EXECUTOR ENDPOINTS ---
from .hermes_executor import discover_hermes_api, hermes_health, send_hermes_job, get_hermes_job, get_all_jobs

@router.get("/executor/status")
async def get_executor_status():
    return hermes_health()

class ExecutorRequest(BaseModel):
    command: str
    mode: str = "lab_unlocked"
    context: dict = {}

@router.post("/executor/execute")
async def executor_execute(req: ExecutorRequest):
    return send_hermes_job(req.command, req.mode, req.context)

@router.get("/executor/jobs")
async def executor_jobs():
    jobs = get_all_jobs()
    return {"ok": True, "jobs": jobs}

@router.get("/executor/jobs/{job_id}")
async def executor_job_status(job_id: str):
    return get_hermes_job(job_id)

# --- LAB ENDPOINTS ---

@router.get("/lab/status")
async def get_lab_status(service: HermesService = Depends(get_hermes_service)):
    status = service.get_status()
    capabilities = service.get_capabilities()
    ollama_status = service.get_ollama_status()
    
    return {
        "operation_mode": status.get("automation_mode", "lab_unlocked"),
        "demo_only": False,
        "real_automation_enabled": True,
        "provider": status.get("llm_provider", "ollama"),
        "model": "qwen2.5:32b-instruct",
        "ollama_connected": ollama_status.get("status") == "connected",
        "hermes_connected": "connected" in status.get("status", ""),
        "browser_provider": detect_browser_provider(),
        "firecrawl_provider": detect_firecrawl(),
        "hermes_executor": discover_hermes_api().get("mode", "offline"),
        "token_exposed": False
    }

@router.post("/lab/test-ollama")
async def test_lab_ollama(service: HermesService = Depends(get_hermes_service)):
    req = HermesExecuteRequest(command="Ollama, responda apenas: QWEN32_OK", mode="lab_unlocked")
    res = service.execute_command(req)
    return res

@router.post("/lab/test-hermes")
async def test_lab_hermes(service: HermesService = Depends(get_hermes_service)):
    req = HermesExecuteRequest(command="test connection", mode="lab_unlocked")
    res = service.execute_command(req)
    return res

@router.post("/lab/execute", response_model=HermesCommandResponse)
async def lab_execute(request: HermesExecuteRequest, service: HermesService = Depends(get_hermes_service)):
    request.mode = "lab_unlocked"
    return service.execute_command(request)

@router.get("/lab/models")
async def get_lab_models(service: HermesService = Depends(get_hermes_service)):
    return {"models": ["qwen2.5:32b-instruct", "qwen2.5:32b", "hermes3:latest"], "default": "qwen2.5:32b-instruct"}

@router.get("/lab/capabilities")
async def get_lab_capabilities(service: HermesService = Depends(get_hermes_service)):
    return service.get_capabilities()

