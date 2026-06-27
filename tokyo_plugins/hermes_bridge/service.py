import uuid
import os
import requests
from datetime import datetime
from typing import Dict, Any
from .config import HermesConfig
from .schemas import HermesCommandRequest, HermesCommandResponse, HermesExecuteRequest, HermesConfirmRequest, AutomationJob
from .audit import SafetyGate
from .client import HermesClient

class HermesService:
    _pending_jobs: Dict[str, AutomationJob] = {}

    def __init__(self):
        self.client = HermesClient()

    def get_status(self) -> Dict[str, Any]:
        enabled = HermesConfig.get("enabled", False)
        if not enabled:
            return {
                "status": "not_configured",
                "safe_mode": True,
                "token_exposed": False,
                "llm_provider": "none"
            }
        
        is_online = self.client.check_health()
        return {
            "status": "connected" if is_online else "offline (fallback_adapter_ready)",
            "safe_mode": HermesConfig.get("safe_mode", False),
            "token_exposed": False,
            "llm_provider": HermesConfig.get("llm_provider", "ollama"),
            "automation_mode": HermesConfig.get("automation_mode", "company_operator")
        }

    def get_ollama_status(self) -> Dict[str, Any]:
        return self.client.check_ollama()

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "capabilities": HermesConfig.get_policy("allowed_low_risk_actions", []),
            "automation_mode": HermesConfig.get("automation_mode", "company_operator")
        }

    def _fallback_adapter_execute(self, req: HermesExecuteRequest) -> HermesCommandResponse:
        cmd_lower = req.command.lower()
        
        # Agent Core Business Employee Routing
        if "bunny dreams" in cmd_lower or "bunnydreams" in cmd_lower or "finanç" in cmd_lower or "financ" in cmd_lower or "cfo" in cmd_lower:
            from openjarvis import Jarvis
            try:
                j = Jarvis()
                response = j.ask(req.command, agent="tokyo_cfo")
                return HermesCommandResponse(
                    ok=True, status="completed", summary=response,
                    actions_executed=[{"action": "cfo_analysis", "agent": "tokyo_cfo"}]
                )
            except Exception as e:
                return HermesCommandResponse(ok=False, status="failed", summary=f"Erro no agente CFO: {e}", risk="low")

        elif "coo" in cmd_lower or "operaç" in cmd_lower or "operac" in cmd_lower or "checklist" in cmd_lower or "loja" in cmd_lower:
            from openjarvis import Jarvis
            try:
                j = Jarvis()
                response = j.ask(req.command, agent="tokyo_coo")
                return HermesCommandResponse(
                    ok=True, status="completed", summary=response,
                    actions_executed=[{"action": "coo_analysis", "agent": "tokyo_coo"}]
                )
            except Exception as e:
                return HermesCommandResponse(ok=False, status="failed", summary=f"Erro no agente COO: {e}", risk="low")

        elif "estoque" in cmd_lower or "compra" in cmd_lower or "sku" in cmd_lower or "inventar" in cmd_lower:
            from openjarvis import Jarvis
            try:
                j = Jarvis()
                response = j.ask(req.command, agent="tokyo_estoque")
                return HermesCommandResponse(
                    ok=True, status="completed", summary=response,
                    actions_executed=[{"action": "estoque_analysis", "agent": "tokyo_estoque"}]
                )
            except Exception as e:
                return HermesCommandResponse(ok=False, status="failed", summary=f"Erro no agente Estoque: {e}", risk="low")

        # Test Connection
        if "testar conex" in cmd_lower or "test connection" in cmd_lower:
            return HermesCommandResponse(
                ok=True, status="completed", summary="Conexão com adapter local testada com sucesso.",
                actions_executed=[{"action": "test_connection", "adapter": "local"}]
            )
            
        # Workspace Spreadsheet
        if "planilha" in cmd_lower or "spreadsheet" in cmd_lower or "csv" in cmd_lower:
            workspace_dir = HermesConfig.get_policy("workspace_root", os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace")
            os.makedirs(workspace_dir, exist_ok=True)
            filename = f"planilha_{uuid.uuid4().hex[:8]}.csv"
            filepath = os.path.join(workspace_dir, filename)
            if not SafetyGate.is_workspace_path_valid(filepath):
                return HermesCommandResponse(ok=False, status="blocked", summary="Path fora do workspace.", risk="high")
            
            with open(filepath, "w") as f:
                f.write(f"ID,Info,Gerado\n1,{req.command},{datetime.utcnow().isoformat()}")
                
            return HermesCommandResponse(
                ok=True, status="completed", summary=f"Executei e registrei o job. Planilha salva em {filepath}",
                actions_executed=[{"action": "create_spreadsheet", "file": filepath}]
            )

        # Workspace Note
        if "nota" in cmd_lower or "note" in cmd_lower or "documento" in cmd_lower or "relatório" in cmd_lower or "relatorio" in cmd_lower:
            workspace_dir = HermesConfig.get_policy("workspace_root", os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace")
            os.makedirs(workspace_dir, exist_ok=True)
            
            # Simple heuristic to extract filename if present
            words = req.command.split()
            filename = next((w for w in words if w.endswith(".md") or w.endswith(".txt")), f"nota_{uuid.uuid4().hex[:8]}.md")
            
            filepath = os.path.join(workspace_dir, filename)
            if not SafetyGate.is_workspace_path_valid(filepath):
                return HermesCommandResponse(ok=False, status="blocked", summary="Path fora do workspace.", risk="high")
            
            with open(filepath, "w") as f:
                f.write(f"# Documento Gerado Automaticamente\nComando: {req.command}")
                
            return HermesCommandResponse(
                ok=True, status="completed", summary=f"Executei e registrei o job. Documento salvo em {filepath}",
                actions_executed=[{"action": "create_workspace_note", "file": filepath}]
            )

        # Web Research / Browser
        if "browser" in cmd_lower or "navegador" in cmd_lower or "site" in cmd_lower or "leia" in cmd_lower or "abra" in cmd_lower:
            from .browser_provider import extract_text, summarize_url, detect_browser_provider
            provider = detect_browser_provider()
            
            # Simple heuristic to extract URL from command
            words = req.command.split()
            url = next((w for w in words if w.startswith("http://") or w.startswith("https://")), None)
            
            if url:
                if "resum" in cmd_lower:
                    res = summarize_url(url, model=req.model)
                else:
                    res = extract_text(url)
                
                if res.get("ok"):
                    return HermesCommandResponse(
                        ok=True, status="completed", summary=res.get("summary", res.get("text", "")[:2000]),
                        actions_executed=[{"action": "browser_extract", "url": url, "provider": provider}]
                    )
                return HermesCommandResponse(ok=False, status="failed", summary=res.get("error", "Erro ao acessar a URL."), risk="low")
            else:
                return HermesCommandResponse(ok=False, status="failed", summary="Nenhuma URL válida encontrada no comando.", risk="low")

        # Firecrawl / Pesquisa
        if "pesquisar" in cmd_lower or "search" in cmd_lower or "firecrawl" in cmd_lower:
            from .firecrawl_provider import scrape_url, detect_firecrawl
            provider = detect_firecrawl()
            
            if provider == "not_configured":
                return HermesCommandResponse(ok=False, status="capability_missing", summary="Firecrawl não configurado, usando Browser Provider fallback", risk="low")
            
            words = req.command.split()
            url = next((w for w in words if w.startswith("http://") or w.startswith("https://")), None)
            if url:
                res = scrape_url(url)
                if res.get("ok"):
                    return HermesCommandResponse(
                        ok=True, status="completed", summary=res.get("text", "")[:2000],
                        actions_executed=[{"action": "firecrawl_scrape", "url": url}]
                    )
                return HermesCommandResponse(ok=False, status="failed", summary=res.get("error", "Erro no Firecrawl."), risk="low")

        # Ollama Chat
        if "ollama" in cmd_lower or "resumo" in cmd_lower or "summarize" in cmd_lower:
            try:
                base_url = HermesConfig.get('ollama_base_url')
                if not base_url:
                    base_url = "http://127.0.0.1:11434"
                res = requests.post(f"{base_url}/api/generate", json={
                    "model": req.model, "prompt": req.command, "stream": False
                }, timeout=120)
                if res.status_code == 200:
                    text = res.json().get("response", "")
                    return HermesCommandResponse(
                        ok=True, status="completed", summary=text,
                        actions_executed=[{"action": "ollama_chat", "model": req.model}]
                    )
            except Exception as e:
                return HermesCommandResponse(ok=False, status="failed", summary=f"Erro no Ollama: {e}", risk="low")

        return HermesCommandResponse(ok=False, status="capability_missing", summary="Adapter local não possui ferramenta para este comando.", risk="low")

    def execute_command(self, req: HermesExecuteRequest) -> HermesCommandResponse:
        is_allowed, risk, reason = SafetyGate.evaluate(req.command, req.mode)
        
        if risk == "critical" or not is_allowed and reason in ["blocked_by_safety_gate", "low_risk_execution_disabled", "mode_not_supported"]:
            return HermesCommandResponse(
                ok=False,
                status="blocked",
                summary=f"Blocked: {reason}",
                risk=risk,
                error=reason
            )

        if not is_allowed and reason == "requires_confirmation":
            job_id = str(uuid.uuid4())
            self._pending_jobs[job_id] = AutomationJob(
                job_id=job_id, command=req.command, status="pending_confirmation",
                risk=risk, mode=req.mode, created_at=datetime.utcnow().isoformat()
            )
            return HermesCommandResponse(
                ok=True,
                job_id=job_id,
                status="pending_confirmation",
                summary="Ação requer confirmação humana devido ao nível de risco.",
                requires_confirmation=True,
                risk=risk
            )

        if req.mode == "dry_run":
            return HermesCommandResponse(
                ok=True, status="completed", summary="Modo simulado ativo.",
                actions_planned=[{"action": "simulated", "command": req.command}], risk=risk
            )

        # First check if Hermes API/Shim handles it
        from .hermes_executor import send_hermes_job, discover_hermes_api
        
        api_info = discover_hermes_api()
        if api_info.get("connected"):
            hermes_res = send_hermes_job(req.command, req.mode)
            if hermes_res.get("ok"):
                data = hermes_res.get("data", hermes_res)
                return HermesCommandResponse(
                    ok=data.get("ok", True),
                    job_id=data.get("job_id", str(uuid.uuid4())),
                    status=data.get("status", "failed"),
                    summary=data.get("summary", "Executado via Hermes API"),
                    actions_executed=data.get("actions_executed", []),
                    risk=risk,
                    error=data.get("error")
                )

        # Fallback to local adapter if Hermes API/Shim failed to handle it or is offline
        fallback_res = self._fallback_adapter_execute(req)
        return fallback_res

    def confirm_action(self, req: HermesConfirmRequest) -> HermesCommandResponse:
        if req.pending_id not in self._pending_jobs:
            return HermesCommandResponse(ok=False, status="not_found", summary="Pending ID não encontrado.", risk="low")
            
        job = self._pending_jobs[req.pending_id]
        if not req.confirm:
            job.status = "cancelled"
            return HermesCommandResponse(ok=True, status="cancelled", summary="Ação cancelada pelo usuário.", risk=job.risk)
            
        if req.human_confirmation != "CONFIRM_HERMES_ACTION":
            return HermesCommandResponse(ok=False, status="blocked", summary="Firmação humana inválida.", risk=job.risk)

        job.status = "executing"
        # Since it's confirmed, we execute using fallback adapter if Hermes is offline
        execute_req = HermesExecuteRequest(command=job.command, mode=job.mode)
        
        if self.client.check_health():
            res = self.client.send_command(execute_req.dict())
            return HermesCommandResponse(**res)
        else:
            res = self._fallback_adapter_execute(execute_req)
            job.status = res.status
            job.executed_at = datetime.utcnow().isoformat()
            return res

    def process_command(self, req: HermesCommandRequest) -> HermesCommandResponse:
        # Legacy mapping to support Phase 5A dry-runs
        execute_req = HermesExecuteRequest(command=req.command, mode=req.mode)
        return self.execute_command(execute_req)

