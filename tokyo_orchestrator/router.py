import os
import json
import requests
import datetime
import uuid

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL") or "http://192.168.1.173:11434"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL") or "qwen2.5:32b-instruct"

SYSTEM_PROMPT = """Você é a TokyoOS, a orquestradora central de inteligência artificial.
O seu trabalho é interpretar a instrução natural do usuário e decidir qual ação técnica tomar.
Você DEVE SEMPRE responder EXATAMENTE e APENAS com um objeto JSON válido, sem NENHUM texto adicional antes ou depois.

Ferramentas Disponíveis (Tools):
1. "mac_open_url": Abre uma URL no Mac Mini (Ex: "Abre o youtube no Mac", "Acesse globo.com"). Requer parâmetro: "url" (str).
2. "mac_reveal_folder": Abre ou mostra uma pasta no Mac Mini. Requer parâmetro: "path" (str).
3. "mac_show_notification": Mostra uma notificação nativa no Mac. Requer parâmetro: "text" (str).
4. "web_search": Faz uma pesquisa real na internet (Ex: "Pesquise quem ganhou o oscar", "Procure sobre IA"). Requer parâmetro: "query" (str).
5. "web_extract": Acessa um site para extrair e ler o conteúdo, e.g., para resumir (Ex: "Leia o site e resuma", "Acesse globo.com e me diga as notícias"). Requer parâmetro: "url" (str), e opcional "summarize" (bool).
6. "workspace_create_file": Cria um arquivo de texto, csv ou md no workspace (Ex: "Crie uma planilha", "Crie um relatorio.md com X"). Requer parâmetros: "filename" (str) e "content" (str).
7. "unknown": Se a intenção não se encaixa nas outras ferramentas.

Formato esperado de saída (JSON estrito):
{
    "tool": "nome_da_ferramenta_aqui",
    "parameters": {
        "chave": "valor"
    }
}
"""

def parse_intent(command: str) -> dict:
    """
    Sends the user command to Ollama to parse the intent using the System Prompt.
    Returns the parsed JSON dict or a fallback "unknown" tool if it fails.
    """
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": command}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            return json.loads(content)
        else:
            return {"tool": "error", "parameters": {"error": f"Ollama HTTP {resp.status_code}"}}
    except Exception as e:
        return {"tool": "error", "parameters": {"error": str(e)}}

def route_command(command: str) -> dict:
    """
    The main Action Gateway router. Parses the intent via LLM and routes to the correct module.
    """
    cmd_lower = command.lower()
    job_id = str(uuid.uuid4())
    
    # Agent Core Business Employee Routing
    if "bunny dreams" in cmd_lower or "bunnydreams" in cmd_lower or "finanç" in cmd_lower or "financ" in cmd_lower or "cfo" in cmd_lower:
        from openjarvis import Jarvis
        try:
            j = Jarvis()
            response = j.ask(command, agent="tokyo_cfo")
            return {
                "ok": True,
                "job_id": job_id,
                "status": "completed",
                "executor": "tokyo_agent_core",
                "provider_used": "tokyo_cfo",
                "summary": response,
                "result": {"agent": "tokyo_cfo", "query": command},
                "logs_sanitized": [f"Routed command to tokyo_cfo Agent"],
                "token_exposed": False
            }
        except Exception as e:
            return {
                "ok": False,
                "job_id": job_id,
                "status": "failed",
                "executor": "tokyo_agent_core",
                "provider_used": "tokyo_cfo",
                "summary": f"Erro no agente CFO: {e}",
                "result": {},
                "logs_sanitized": [f"Failed to route to tokyo_cfo: {e}"],
                "token_exposed": False
            }

    elif "coo" in cmd_lower or "operaç" in cmd_lower or "operac" in cmd_lower or "checklist" in cmd_lower or "loja" in cmd_lower:
        from openjarvis import Jarvis
        try:
            j = Jarvis()
            response = j.ask(command, agent="tokyo_coo")
            return {
                "ok": True,
                "job_id": job_id,
                "status": "completed",
                "executor": "tokyo_agent_core",
                "provider_used": "tokyo_coo",
                "summary": response,
                "result": {"agent": "tokyo_coo", "query": command},
                "logs_sanitized": [f"Routed command to tokyo_coo Agent"],
                "token_exposed": False
            }
        except Exception as e:
            return {
                "ok": False,
                "job_id": job_id,
                "status": "failed",
                "executor": "tokyo_agent_core",
                "provider_used": "tokyo_coo",
                "summary": f"Erro no agente COO: {e}",
                "result": {},
                "logs_sanitized": [f"Failed to route to tokyo_coo: {e}"],
                "token_exposed": False
            }

    elif "estoque" in cmd_lower or "compra" in cmd_lower or "sku" in cmd_lower or "inventar" in cmd_lower:
        from openjarvis import Jarvis
        try:
            j = Jarvis()
            response = j.ask(command, agent="tokyo_estoque")
            return {
                "ok": True,
                "job_id": job_id,
                "status": "completed",
                "executor": "tokyo_agent_core",
                "provider_used": "tokyo_estoque",
                "summary": response,
                "result": {"agent": "tokyo_estoque", "query": command},
                "logs_sanitized": [f"Routed command to tokyo_estoque Agent"],
                "token_exposed": False
            }
        except Exception as e:
            return {
                "ok": False,
                "job_id": job_id,
                "status": "failed",
                "executor": "tokyo_agent_core",
                "provider_used": "tokyo_estoque",
                "summary": f"Erro no agente Estoque: {e}",
                "result": {},
                "logs_sanitized": [f"Failed to route to tokyo_estoque: {e}"],
                "token_exposed": False
            }

    # 1. Obter a intenção via LLM
    intent = parse_intent(command)
    tool = intent.get("tool", "unknown")
    params = intent.get("parameters", {})
    
    # Pre-configure fallback job structures
    status = "completed"
    ok = True
    summary = ""
    provider_used = "tokyo_orchestrator"
    
    try:
        # 2. Executar a ação baseado na ferramenta escolhida
        if tool == "mac_open_url":
            from tokyo_mac_bridge.bridge_service import MacBridgeService
            mac_svc = MacBridgeService()
            url = params.get("url", "https://google.com")
            if not url.startswith("http"): url = "https://" + url
            res = mac_svc.process_command("open_url", {"url": url})
            return res  # MacBridge returns the proper response format
            
        elif tool == "mac_reveal_folder":
            from tokyo_mac_bridge.bridge_service import MacBridgeService
            mac_svc = MacBridgeService()
            path = params.get("path", "/Users/Shared")
            res = mac_svc.process_command("reveal_folder", {"path": path})
            return res
            
        elif tool == "mac_show_notification":
            from tokyo_mac_bridge.bridge_service import MacBridgeService
            mac_svc = MacBridgeService()
            text = params.get("text", "Olá")
            res = mac_svc.process_command("show_notification", {"text": text})
            return res
            
        elif tool == "web_search":
            from tokyo_plugins.hermes_bridge.browser_provider import search_web
            query = params.get("query", "")
            res = search_web(query)
            ok = res.get("ok", False)
            summary = res.get("text", res.get("error", "Erro na pesquisa"))
            provider_used = "hermes_browser_search"
            if not ok: status = "failed"
            
        elif tool == "web_extract":
            from tokyo_plugins.hermes_bridge.browser_provider import extract_text, summarize_url
            url = params.get("url", "")
            summarize = params.get("summarize", False)
            if summarize:
                res = summarize_url(url, model=OLLAMA_MODEL)
            else:
                res = extract_text(url)
            ok = res.get("ok", False)
            summary = res.get("summary", res.get("text", res.get("error", "Erro de extração")))
            provider_used = "hermes_browser_extract"
            if not ok: status = "failed"
            
        elif tool == "workspace_create_file":
            filename = params.get("filename", f"file_{job_id[:8]}.txt")
            content = params.get("content", "")
            workspace_dir = os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace"
            os.makedirs(workspace_dir, exist_ok=True)
            filepath = os.path.join(workspace_dir, filename)
            with open(filepath, "w") as f:
                f.write(content)
            summary = f"Arquivo criado com sucesso: {filename}"
            provider_used = "tokyo_workspace"
            
        else:
            ok = False
            status = "failed"
            summary = f"Ferramenta desconhecida ou erro de IA: {tool} - {params.get('error', '')}"
            
    except Exception as e:
        ok = False
        status = "failed"
        summary = f"Erro fatal ao executar roteamento: {e}"
        
    # Return the standardized response
    return {
        "ok": ok,
        "job_id": job_id,
        "status": status,
        "executor": "tokyo_orchestrator",
        "provider_used": provider_used,
        "summary": summary[:2000] if summary else "",
        "result": intent,
        "logs_sanitized": [f"LLM Orchestrator routed command to: {tool}"],
        "token_exposed": False
    }
