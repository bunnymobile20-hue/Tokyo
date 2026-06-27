import os
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx


from finance_engine import (
    calculate_dre, calculate_cash_flow, calculate_break_even,
    calculate_operational_cycle, calculate_financial_cycle, calculate_minimum_cash,
)
from finance_engine.audit import log as audit_log

from siberian_connector import client as siberian_client
from siberian_connector.routes import router as siberian_router
from tokyo_plugins.hermes_bridge.routes import router as hermes_router
from tokyo_agent_core.routes import router as agent_core_router
from tokyo_openjarvis_bridge.router import router as bridge_router
from tokyo_openjarvis_bridge.health import router as bridge_health_router
from tokyo_dashboards.routes import router as dashboards_router

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tokyoos")

BASE_DIR = Path(__file__).parent
os.environ.setdefault("OPENJARVIS_HOME", str(BASE_DIR / "data" / "openjarvis"))
CONFIG_DIR = BASE_DIR / "config"
INTERFACE_DIR = BASE_DIR / "interface"
DOCS_DIR = BASE_DIR / "docs"

TOKYO_ENV = os.getenv("TOKYO_ENV", "zimaos")
TOKYO_HOST = os.getenv("TOKYO_HOST", "0.0.0.0")
TOKYO_HTTP_PORT = int(os.getenv("TOKYO_HTTP_PORT", "8788"))
TOKYO_SAFE_MODE = os.getenv("TOKYO_SAFE_MODE", "false").lower() == "true"
TOKYO_TOKEN_EXPOSED = os.getenv("TOKYO_TOKEN_EXPOSED", "false").lower() == "true"

app = FastAPI(
    title="TokyoOS",
    description="Tokyo IA - GrupsBunny AI Hub — Phase 5A Hermes Integration",
    version="5.0.0-phase5a",
    docs_url="/tokyo/docs",
    redoc_url="/tokyo/redoc",
)

class OIRewriteMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/oi/"):
            scope["path"] = "/" + scope["path"][4:]
            if "raw_path" in scope:
                scope["raw_path"] = scope["path"].encode("ascii")
        await self.app(scope, receive, send)

app.add_middleware(OIRewriteMiddleware)

app.include_router(siberian_router)
app.include_router(hermes_router)
app.include_router(bridge_router)
app.include_router(bridge_health_router, prefix="/tokyo/bridge")
app.include_router(agent_core_router)
app.include_router(dashboards_router)

from openjarvis.server.desktop_agent_router import router as desktop_agent_router, operator_router
app.include_router(desktop_agent_router)
app.include_router(operator_router)

from openjarvis.server.api_routes import include_all_routes
from openjarvis.server.routes import router as oj_router
from openjarvis.engine.ollama import OllamaEngine

app.state.engine = OllamaEngine(host="http://192.168.1.173:11434")
app.state.engine_name = "ollama"

include_all_routes(app)
app.include_router(oj_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_json_config(filename):
    path = CONFIG_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def safe_response(data):
    data["_meta"] = {
        "token_exposed": TOKYO_TOKEN_EXPOSED,
        "safe_mode": TOKYO_SAFE_MODE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tokyo_version": "3.2.0-phase3c",
        "status": "SAFE_TO_CONTINUE_PHASE_3C_ZIMAOS_READY",
    }
    response = JSONResponse(content=data)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def env_bool(name, default=False):
    return os.getenv(name, str(default).lower()).lower() in ("true", "1", "yes")


def env_present(name):
    val = os.getenv(name, "")
    return len(val) > 0


def mask_secret(val):
    if not val:
        return ""
    return val[:4] + "***" if len(val) > 8 else "***"


FRONTEND_DIR = BASE_DIR / "src" / "openjarvis" / "server" / "static"
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
@app.get("/ui/", response_class=HTMLResponse)
@app.get("/ui/{module:path}", response_class=HTMLResponse)
async def serve_ui(module: str = None):
    ui_file = INTERFACE_DIR / "index.html"
    if ui_file.exists():
        return HTMLResponse(content=ui_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>TokyoOS UI not found. Please build frontend.</h1>", status_code=404)

@app.get("/chat-local", response_class=HTMLResponse)
@app.get("/chat-local/", response_class=HTMLResponse)
@app.get("/chat-local/{module:path}", response_class=HTMLResponse)
async def serve_chat_local(module: str = None):
    ui_file = FRONTEND_DIR / "index.html"
    if ui_file.exists():
        return HTMLResponse(content=ui_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Chat Local not found. Please build frontend.</h1>", status_code=404)


@app.get("/tokyo/system/health")
async def system_health():
    return safe_response({
        "health": "ok",
        "environment": TOKYO_ENV,
        "uptime": "active",
        "voice_preserved": True,
        "app_preserved": True,
        "safe_mode": TOKYO_SAFE_MODE,
    })


@app.get("/tokyo/setup/status")
async def setup_status():
    return safe_response({
        "setup_complete": False,
        "wizard_available": True,
        "first_config_done": False,
        "env_validated": bool(load_dotenv()),
        "credentials_checked": False,
        "integrations_checked": False,
        "providers_checked": False,
        "steps": {
            "env_validation": "pending_first_run",
            "credentials_status": "pending",
            "integrations_status": "pending",
            "providers_status": "pending",
            "storage_check": "pending",
            "voice_check": "pending",
            "security_check": "pending",
            "docker_readiness": "pending",
        },
    })


@app.get("/tokyo/setup/checklist")
async def setup_checklist():
    return safe_response({
        "checklist": [
            {"id": "env_file", "label": ".env configurado", "status": "pending", "detail": "Configure as variaveis no .env"},
            {"id": "gemini_key", "label": "Gemini API Key", "status": "configured" if env_present("GEMINI_API_KEY") else "not_configured", "detail": "Motor LLM principal recomendado"},
            {"id": "openai_key", "label": "OpenAI API Key", "status": "configured" if env_present("OPENAI_API_KEY") else "not_configured", "detail": "Motor LLM fallback"},
            {"id": "livekit", "label": "LiveKit Voice", "status": "configured" if env_present("LIVEKIT_URL") else "not_configured", "detail": "Voz oficial Tokyo"},
            {"id": "memory", "label": "Memoria (Mem0/Local)", "status": "configured" if env_present("MEM0_API_KEY") else "configured_local", "detail": "Memoria da Tokyo"},
            {"id": "siberian", "label": "Sistema Siberian ERP", "status": "not_configured", "detail": "ERP proprio do GrupsBunny"},
            {"id": "security", "label": "Seguranca", "status": "configured" if TOKYO_SAFE_MODE else "not_configured", "detail": "Safe mode ativo"},
            {"id": "docker", "label": "Docker/ZimaOS", "status": "pending", "detail": "Preparar para deploy 24/7"},
        ],
    })


@app.get("/tokyo/doctor")
async def doctor():
    agent_core_active = False
    rust_available = False
    try:
        from openjarvis import Jarvis
        from openjarvis.core.registry import AgentRegistry
        from tokyo_agent_core._rust_bridge import RUST_AVAILABLE
        import openjarvis.agents # triggers registration
        rust_available = RUST_AVAILABLE
        # Instantiate to check initialization
        j = Jarvis()
        if AgentRegistry.contains("tokyo_cfo"):
            agent_core_active = True
    except Exception:
        pass

    return safe_response({
        "status": "healthy_with_pending_items" if agent_core_active else "warning",
        "checks": {
            "system": {"status": "healthy", "detail": "TokyoOS rodando"},
            "ui": {"status": "healthy", "detail": "Interface disponivel"},
            "voice": {"status": "healthy" if env_present("LIVEKIT_URL") else "not_configured", "detail": "LiveKit voice agent"},
            "gemini": {"status": "configured" if env_present("GEMINI_API_KEY") else "not_configured", "detail": "Google Gemini provider"},
            "openai": {"status": "configured" if env_present("OPENAI_API_KEY") else "not_configured", "detail": "OpenAI provider"},
            "memory": {"status": "healthy", "detail": "Local memory enabled"},
            "mem0": {"status": "configured" if env_present("MEM0_API_KEY") else "not_configured", "detail": "Mem0 cloud memory"},
            "storage": {"status": "healthy" if os.access(os.getenv("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace", os.W_OK | os.R_OK) else "warning", "detail": "Workspace storage OK" if os.access(os.getenv("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace", os.W_OK | os.R_OK) else "Workspace permissões falharam"},
            "security": {"status": "secure" if TOKYO_SAFE_MODE else "warning", "detail": "Safe mode " + ("enabled" if TOKYO_SAFE_MODE else "disabled")},
            "docker": {"status": "pending", "detail": "Docker/ZimaOS deployment pending"},
            "siberian": {"status": "not_configured", "detail": "Sistema Siberian not connected"},
            "integrations": {"status": "pending", "detail": "Optional integrations not configured"},
            "agent_core": {"status": "healthy" if agent_core_active else "error", "detail": "Agent Core (OpenJarvis) carregado com sucesso" if agent_core_active else "Falha ao carregar Agent Core"},
            "rust_bridge": {"status": "healthy" if rust_available else "warning", "detail": "Suporte a compilacao Rust ativo" if rust_available else "Compilacao Rust indisponivel (usando fallbacks Python local)"}
        },
        "recommendations": [
            "Configurar GEMINI_API_KEY para LLM principal",
            "Configurar LIVEKIT_URL para voz",
            "Sistema Siberian nao requer configuracao nesta fase",
            "Integracoes opcionais (Hermes, MCP, Ollama) nao sao obrigatorias",
            "Acesse a aba 'Funcionarios IA' na interface para testar os agentes CFO, COO e Estoque"
        ],
    })


@app.get("/tokyo/llm/status")
async def llm_status():
    providers_config = load_json_config("providers.example.json")
    return safe_response({
        "default_provider": os.getenv("TOKYO_DEFAULT_LLM_PROVIDER", "gemini"),
        "fallback_provider": os.getenv("TOKYO_FALLBACK_LLM_PROVIDER", "openai"),
        "providers": {
            "gemini": {
                "configured": env_present("GEMINI_API_KEY"),
                "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                "status": "configured" if env_present("GEMINI_API_KEY") else "not_configured",
                "voice_support": True,
                "realtime_support": True,
            },
            "openai": {
                "configured": env_present("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "status": "configured" if env_present("OPENAI_API_KEY") else "not_configured",
                "voice_support": True,
                "realtime_support": False,
            },
            "openai_compatible": {
                "configured": env_present("OPENAI_COMPATIBLE_BASE_URL"),
                "model": os.getenv("OPENAI_COMPATIBLE_MODEL", ""),
                "status": "configured" if env_present("OPENAI_COMPATIBLE_BASE_URL") else "not_configured",
            },
            "ollama": {
                "configured": env_present("OLLAMA_BASE_URL"),
                "status": "configured" if env_present("OLLAMA_BASE_URL") else "not_configured",
                "required": False,
                "mode": "optional",
            },
            "openwebui": {
                "configured": env_present("OPENWEBUI_BASE_URL"),
                "status": "configured" if env_present("OPENWEBUI_BASE_URL") else "not_configured",
                "required": False,
                "mode": "optional",
            },
        },
        "token_exposed": TOKYO_TOKEN_EXPOSED,
        "voice_preserved": True,
    })

# --- OLLAMA ENDPOINTS ---
@app.get("/tokyo/plugins/ollama/models")
async def ollama_models():
    from tokyo_agent_core.llm_manager import llm_manager
    models = llm_manager.list_local_models()
    hardware = llm_manager.detect_hardware()
    return safe_response({"models": models, "hardware": hardware})

@app.post("/tokyo/plugins/ollama/pull")
async def ollama_pull(request: Request):
    try:
        data = await request.json()
        model_name = data.get("model")
        if not model_name:
            return safe_response({"success": False, "error": "No model name provided"})
            
        from tokyo_agent_core.llm_manager import llm_manager
        success = llm_manager.pull_model(model_name)
        return safe_response({"success": success})
    except Exception as e:
        return safe_response({"success": False, "error": str(e)})

@app.post("/tokyo/plugins/ollama/assign")
async def ollama_assign(request: Request):
    try:
        data = await request.json()
        agent_id = data.get("agent_id")
        model_name = data.get("model")
        if not agent_id or not model_name:
            return safe_response({"success": False, "error": "Missing agent_id or model"})
            
        from tokyo_agent_core.llm_manager import llm_manager
        llm_manager.set_model_for_agent(agent_id, model_name)
        return safe_response({"success": True})
    except Exception as e:
        return safe_response({"success": False, "error": str(e)})

@app.get("/tokyo/providers/registry")
async def providers_registry():
    config = load_json_config("providers.example.json")
    if config:
        return safe_response(config)
    return safe_response({"error": "Providers config not found", "providers": []})


@app.get("/tokyo/providers/status")
async def providers_status():
    return safe_response({
        "providers": [
            {"id": "gemini", "configured": env_present("GEMINI_API_KEY"), "status": "configured" if env_present("GEMINI_API_KEY") else "not_configured"},
            {"id": "openai", "configured": env_present("OPENAI_API_KEY"), "status": "configured" if env_present("OPENAI_API_KEY") else "not_configured"},
            {"id": "openai_compatible", "configured": env_present("OPENAI_COMPATIBLE_BASE_URL"), "status": "configured" if env_present("OPENAI_COMPATIBLE_BASE_URL") else "not_configured"},
            {"id": "ollama", "configured": env_present("OLLAMA_BASE_URL"), "required": False, "status": "configured" if env_present("OLLAMA_BASE_URL") else "not_configured"},
            {"id": "openwebui", "configured": env_present("OPENWEBUI_BASE_URL"), "required": False, "status": "configured" if env_present("OPENWEBUI_BASE_URL") else "not_configured"},
        ],
    })


@app.get("/tokyo/integrations/registry")
async def integrations_registry():
    config = load_json_config("integrations.example.json")
    if config:
        return safe_response(config)
    return safe_response({"error": "Integrations config not found", "integrations": []})


@app.get("/tokyo/integrations/status")
async def integrations_status():
    config = load_json_config("integrations.example.json")
    overview = []
    if config:
        for integration in config.get("integrations", []):
            item = {
                "id": integration["id"],
                "name": integration["name"],
                "category": integration["category"],
                "required": integration.get("required", False),
                "status": integration.get("status", "not_configured"),
                "mode": integration.get("mode", "optional"),
            }
            overview.append(item)
    return safe_response({
        "integrations": overview,
        "total": len(overview),
        "configured": sum(1 for i in overview if i["status"] == "configured"),
        "total_required": sum(1 for i in overview if i.get("required", False)),
    })


@app.get("/tokyo/connectors/registry")
async def connectors_registry():
    config = load_json_config("connectors.example.json")
    if config:
        return safe_response(config)
    return safe_response({"error": "Connectors config not found", "connectors": []})


@app.get("/tokyo/plugins/registry")
async def plugins_registry():
    return safe_response({
        "plugins": [
            {
                "id": "hermes_bridge",
                "name": "Hermes Agent Bridge",
                "status": "active",
                "safe_mode": TOKYO_SAFE_MODE
            }
        ],
        "connectors": True,
        "api_hub": True,
        "message": "Plugins use same registry as connectors. See /tokyo/connectors/registry",
    })


@app.get("/tokyo/api-hub/status")
async def api_hub_status():
    return safe_response({
        "api_hub": "Tokyo API Hub",
        "status": "active",
        "description": "Central para conectar APIs externas",
        "principle": "Cada ferramenta tem endpoint/base_url/token_env. Falha de ferramenta opcional nao derruba a TokyoOS.",
        "endpoints_available": [
            "/tokyo/system/health",
            "/tokyo/setup/status",
            "/tokyo/setup/checklist",
            "/tokyo/doctor",
            "/tokyo/llm/status",
            "/tokyo/providers/registry",
            "/tokyo/providers/status",
            "/tokyo/integrations/registry",
            "/tokyo/integrations/status",
            "/tokyo/connectors/registry",
            "/tokyo/plugins/registry",
            "/tokyo/api-hub/status",
            "/tokyo/mcp/status",
            "/tokyo/memory/status",
            "/tokyo/voice/status",
            "/tokyo/security/status",
            "/tokyo/business/status",
            "/tokyo/grupsbunny/status",
            "/tokyo/bunnydreams/status",
            "/tokyo/bunnysiberian/status",
            "/tokyo/siberian/status",
            "/tokyo/finance/status",
            "/tokyo/finance/models",
            "/tokyo/finance/references",
        ],
        "token_exposed": TOKYO_TOKEN_EXPOSED,
    })


@app.get("/tokyo/mcp/status")
async def mcp_status():
    return safe_response({
        "mcp": {
            "enabled": env_bool("MCP_ENABLED"),
            "required": False,
            "status": "configured" if env_present("MCP_BASE_URL") else "not_configured",
            "mode": "optional",
            "safe_mode": TOKYO_SAFE_MODE,
            "default_port": 8789,
            "base_url_configured": env_present("MCP_BASE_URL"),
            "api_key_configured": env_present("MCP_API_KEY"),
            "message": "MCP entra como conector opcional. Nao e core da TokyoOS.",
        }
    })


@app.get("/tokyo/memory/status")
async def memory_status():
    return safe_response({
        "memory": {
            "mem0": {
                "enabled": env_bool("MEM0_ENABLED", True),
                "configured": env_present("MEM0_API_KEY"),
                "status": "configured" if env_present("MEM0_API_KEY") else "not_configured",
                "type": "cloud_memory",
            },
            "obsidian": {
                "enabled": env_bool("OBSIDIAN_ENABLED"),
                "configured": env_present("OBSIDIAN_API_KEY"),
                "status": "configured" if env_present("OBSIDIAN_API_KEY") else "not_configured",
                "vault_path": os.getenv("OBSIDIAN_VAULT_PATH", "/data/tokyo/memory/obsidian"),
                "type": "local_vault",
            },
            "local_memory": {
                "enabled": env_bool("LOCAL_MEMORY_ENABLED", True),
                "status": "configured",
                "path": os.getenv("LOCAL_MEMORY_PATH", "/data/tokyo/memory/local"),
                "type": "local_filesystem",
            },
            "bunny_intelligence": {
                "enabled": env_bool("BUNNY_INTELLIGENCE_ENABLED", True),
                "status": "configured",
                "path": os.getenv("BUNNY_INTELLIGENCE_PATH", "/data/tokyo/intelligence"),
                "type": "document_bank",
            },
        },
        "voice_memory_preserved": True,
        "message": "Mem0 esta integrado ao agente de voz. Memorias preservadas.",
    })


@app.get("/tokyo/voice/status")
async def voice_status():
    return safe_response({
        "voice": {
            "status": "active",
            "provider": "LiveKit",
            "llm": "Google Gemini Realtime",
            "voice_name": "Charon",
            "configured": env_present("LIVEKIT_URL"),
            "livekit_url_configured": env_present("LIVEKIT_URL"),
            "livekit_key_configured": env_present("LIVEKIT_API_KEY"),
            "preserved": True,
            "message": "Voz atual preservada. Nao alterada nesta fase.",
        }
    })


@app.get("/tokyo/security/status")
async def security_status():
    return safe_response({
        "security": {
            "safe_mode": TOKYO_SAFE_MODE,
            "token_exposed": TOKYO_TOKEN_EXPOSED,
            "auth_enabled": env_bool("TOKYO_AUTH_ENABLED", True),
            "admin_configured": env_present("TOKYO_ADMIN_USER"),
            "session_secret_configured": env_present("TOKYO_SESSION_SECRET"),
            "safety_gate": env_bool("SAFETY_GATE_ENABLED", True),
            "confirm_write": env_bool("SAFETY_REQUIRE_CONFIRMATION_FOR_WRITE", True),
            "confirm_delete": env_bool("SAFETY_REQUIRE_CONFIRMATION_FOR_DELETE", True),
            "confirm_finance": env_bool("SAFETY_REQUIRE_CONFIRMATION_FOR_FINANCE", True),
            "confirm_stock": env_bool("SAFETY_REQUIRE_CONFIRMATION_FOR_STOCK", True),
            "confirm_price": env_bool("SAFETY_REQUIRE_CONFIRMATION_FOR_PRICE", True),
            "mask_secrets": env_bool("SAFETY_MASK_SECRETS_IN_LOGS", True),
        },
        "destructive_operations_blocked": True,
        "message": "Operacoes destrutivas bloqueadas. Seguranca preservada.",
    })


@app.get("/tokyo/business/status")
async def business_status():
    config = load_json_config("business.example.json")
    if config:
        return safe_response(config)
    return safe_response({"error": "Business config not found"})


@app.get("/tokyo/grupsbunny/status")
async def grupsbunny_status():
    return safe_response({
        "grupsbunny": {
            "name": "GrupsBunny",
            "type": "holding",
            "status": "active",
            "data_source": "pending_api",
            "companies": [
                {"id": "bunny_dreams", "name": "Bunny Dreams", "type": "retail"},
                {"id": "bunny_siberian", "name": "Bunny Siberian", "type": "systems_company"},
            ],
            "products": [
                {"id": "sistema_siberian", "name": "Sistema Siberian ERP", "type": "own_product"},
            ],
            "dashboard_status": "planned",
            "financial_status": "pending_api",
            "message": "Dados consolidados ainda nao conectados. Configure Sistema Siberian API ou importe planilhas autorizadas.",
        }
    })


@app.get("/tokyo/bunnydreams/status")
async def bunnydreams_status():
    return safe_response({
        "bunny_dreams": {
            "name": "Bunny Dreams",
            "type": "retail",
            "description": "Varejo - Loja de roupas e acessorios",
            "status": "active",
            "data_source": "pending_api",
            "units": [
                {
                    "id": "riverside",
                    "name": "Loja Riverside",
                    "type": "store",
                    "location": "Riverside",
                    "status": "active",
                    "data_source": "pending_api",
                },
                {
                    "id": "teresina",
                    "name": "Loja Teresina",
                    "type": "store",
                    "location": "Teresina",
                    "status": "active",
                    "data_source": "pending_api",
                },
            ],
            "dashboard_modules": [
                "daily_sales", "monthly_sales", "monthly_target", "target_gap",
                "average_ticket", "sales_calendar", "tasks", "stock",
                "critical_products", "financial_dre", "cash_flow", "break_even",
                "minimum_cash", "alerts", "tokyo_recommendations",
            ],
            "message": "Dados de vendas ainda nao conectados. Configure Sistema Siberian API.",
        }
    })


@app.get("/tokyo/bunnysiberian/status")
async def bunnysiberian_status():
    return safe_response({
        "bunny_siberian": {
            "name": "Bunny Siberian",
            "type": "systems_company",
            "description": "Empresa de sistemas - SaaS/ERP B2B",
            "business_model": {
                "type": "recurring_revenue",
                "products": ["sistema_siberian", "consulting", "implementation", "support"],
                "revenue_streams": ["mrr", "implementation_fees", "support_contracts"],
                "metrics": ["mrr", "churn_rate", "ltv", "cac", "arpu"],
            },
            "status": "active",
            "data_source": "pending_api",
            "dashboard_modules": [
                "overview", "recurring_revenue", "active_clients", "mrr",
                "churn", "support_tickets", "implementation_status",
                "sales_funnel", "sold_modules", "api_status", "siberian_erp_status",
            ],
            "message": "Dados da Bunny Siberian ainda nao conectados. Configure Bunny Siberian API.",
        }
    })


@app.get("/tokyo/finance/status")
async def finance_status():
    return safe_response({
        "finance": {
            "status": "planned",
            "data_source": "pending_api",
            "no_fake_data": True,
            "message": "Dados financeiros ainda nao conectados. Configure Sistema Siberian API ou importe planilhas autorizadas.",
            "modules_planned": [
                {"id": "dre", "name": "DRE", "status": "planned"},
                {"id": "cash_flow", "name": "Fluxo de Caixa", "status": "planned"},
                {"id": "break_even", "name": "Ponto de Equilibrio", "status": "planned"},
                {"id": "operational_cycle", "name": "Ciclo Financeiro", "status": "planned"},
                {"id": "minimum_cash", "name": "Caixa Minimo", "status": "planned"},
                {"id": "financial_dashboard", "name": "Dashboard Financeiro", "status": "planned"},
            ],
            "reference_spreadsheets": [
                "Modelo+de+DRE.xlsx",
                "Estrutura+de+DRE.xlsx",
                "Estrutura+de+Fluxo+de+Caixa.xlsx",
                "Ponto de Equilibrio.xlsx",
                "Ciclo Operaciona, Financeiro e Caixa Minimo.xlsx",
                "Ciclo Operaciona, Financeiro e Caixa Minimo (1).xlsx",
            ],
            "reference_status": "recognized_as_business_models",
            "future_upload": {
                "area": "Bunny Intelligence Bank > Planilhas Financeiras",
                "status": "upload_pending_parser_pending",
                "accepted_formats": ["xlsx", "csv", "ods"],
            },
        }
    })


@app.get("/tokyo/finance/models")
async def finance_models():
    config = load_json_config("finance_models.example.json")
    if config:
        return safe_response(config)
    return safe_response({"error": "Finance models config not found"})


@app.get("/tokyo/finance/references")
async def finance_references():
    return safe_response({
        "reference_spreadsheets": [
            {
                "file": "Modelo+de+DRE.xlsx",
                "model_id": "dre",
                "status": "reference_only",
                "message": "Usado como modelo de negocio, nao como dado real",
            },
            {
                "file": "Estrutura+de+DRE.xlsx",
                "model_id": "dre",
                "status": "reference_only",
                "message": "Usado como modelo de negocio, nao como dado real",
            },
            {
                "file": "Estrutura+de+Fluxo+de+Caixa.xlsx",
                "model_id": "cash_flow",
                "status": "reference_only",
                "message": "Usado como modelo de negocio, nao como dado real",
            },
            {
                "file": "Ponto de Equilibrio.xlsx",
                "model_id": "break_even",
                "status": "reference_only",
                "message": "Usado como modelo de negocio, nao como dado real",
            },
            {
                "file": "Ciclo Operaciona, Financeiro e Caixa Minimo.xlsx",
                "model_ids": ["operational_cycle", "minimum_cash"],
                "status": "reference_only",
                "message": "Usado como modelo de negocio, nao como dado real",
            },
            {
                "file": "Ciclo Operaciona, Financeiro e Caixa Minimo (1).xlsx",
                "model_ids": ["operational_cycle", "minimum_cash"],
                "status": "reference_only",
                "message": "Usado como modelo de negocio, nao como dado real",
            },
        ],
        "policy": {
            "no_data_alteration": True,
            "no_overwrite": True,
            "no_fake_values": True,
            "used_as_business_models_only": True,
        },
    })


@app.get("/tokyo/hardware/status")
async def hardware_status():
    return safe_response({
        "hardware_target": {
            "cpu": "Xeon 22 nucleos",
            "gpu": "2x RTX 3060 12GB",
            "ram": "64GB",
            "storage": ["1TB NVMe", "1TB SSD"],
            "platform": "ZimaOS",
            "uptime": "24/7",
        },
        "future_expansion": {
            "mac_mini_m5": {
                "role": "estacao premium/cliente/agente",
                "connector": "apple_macos_agent",
                "status": "planned",
            },
        },
    })


@app.get("/tokyo/update/status")
async def update_status():
    return safe_response({
        "update": {
            "current_version": "3.0.0-phase3a",
            "status": "phase3a_siberian_readonly_api",
            "upgrade_prepared": True,
            "message": "Phase 2 Read-Only Data Layer active. Finance engine, upload center, Siberian connector prepared.",
        }
    })


# ═══════════════════════════════════════════════════════════
# PHASE 2: FINANCE CALCULATION ENDPOINTS
# ═══════════════════════════════════════════════════════════

class DRERequest(BaseModel):
    gross_revenue: Optional[float] = None
    deductions: Optional[float] = None
    cogs: Optional[float] = None
    fixed_expenses: Optional[float] = None
    variable_expenses: Optional[float] = None
    source: str = "manual_input"
    scope: str = "grupsbunny"

class CashFlowRequest(BaseModel):
    opening_balance: Optional[float] = None
    inflows: Optional[float] = None
    outflows: Optional[float] = None
    accounts_receivable: Optional[float] = None
    accounts_payable: Optional[float] = None
    source: str = "manual_input"
    scope: str = "grupsbunny"

class BreakEvenRequest(BaseModel):
    fixed_costs: Optional[float] = None
    contribution_margin_percent: Optional[float] = None
    target_profit: Optional[float] = None
    source: str = "manual_input"
    scope: str = "grupsbunny"

class OperationalCycleRequest(BaseModel):
    average_inventory_days: Optional[float] = None
    average_receivable_days: Optional[float] = None
    source: str = "manual_input"
    scope: str = "grupsbunny"

class FinancialCycleRequest(BaseModel):
    average_inventory_days: Optional[float] = None
    average_receivable_days: Optional[float] = None
    average_payable_days: Optional[float] = None
    source: str = "manual_input"
    scope: str = "grupsbunny"

class MinimumCashRequest(BaseModel):
    daily_cash_need: Optional[float] = None
    financial_cycle_days: Optional[float] = None
    safety_days: Optional[float] = None
    source: str = "manual_input"
    scope: str = "grupsbunny"


@app.post("/tokyo/finance/calculate/dre")
async def finance_calculate_dre(req: DRERequest):
    audit_log("finance_calculation_requested", {"module": "dre", "scope": req.scope, "source": req.source})
    result = calculate_dre(
        gross_revenue=req.gross_revenue,
        deductions=req.deductions,
        cogs=req.cogs,
        fixed_expenses=req.fixed_expenses,
        variable_expenses=req.variable_expenses,
        source=req.source,
        scope=req.scope,
    )
    audit_log("finance_calculation_completed", {"module": "dre", "success": result["success"], "warnings": result["warnings"]})
    return safe_response(result)


@app.post("/tokyo/finance/calculate/cash-flow")
async def finance_calculate_cash_flow(req: CashFlowRequest):
    audit_log("finance_calculation_requested", {"module": "cash_flow", "scope": req.scope, "source": req.source})
    result = calculate_cash_flow(
        opening_balance=req.opening_balance,
        inflows=req.inflows,
        outflows=req.outflows,
        accounts_receivable=req.accounts_receivable,
        accounts_payable=req.accounts_payable,
        source=req.source,
        scope=req.scope,
    )
    audit_log("finance_calculation_completed", {"module": "cash_flow", "success": result["success"], "warnings": result["warnings"]})
    return safe_response(result)


@app.post("/tokyo/finance/calculate/break-even")
async def finance_calculate_break_even(req: BreakEvenRequest):
    audit_log("finance_calculation_requested", {"module": "break_even", "scope": req.scope, "source": req.source})
    result = calculate_break_even(
        fixed_costs=req.fixed_costs,
        contribution_margin_percent=req.contribution_margin_percent,
        target_profit=req.target_profit,
        source=req.source,
        scope=req.scope,
    )
    audit_log("finance_calculation_completed", {"module": "break_even", "success": result["success"], "warnings": result["warnings"]})
    return safe_response(result)


@app.post("/tokyo/finance/calculate/operational-cycle")
async def finance_calculate_operational_cycle(req: OperationalCycleRequest):
    audit_log("finance_calculation_requested", {"module": "operational_cycle", "scope": req.scope, "source": req.source})
    result = calculate_operational_cycle(
        average_inventory_days=req.average_inventory_days,
        average_receivable_days=req.average_receivable_days,
        source=req.source,
        scope=req.scope,
    )
    audit_log("finance_calculation_completed", {"module": "operational_cycle", "success": result["success"], "warnings": result["warnings"]})
    return safe_response(result)


@app.post("/tokyo/finance/calculate/financial-cycle")
async def finance_calculate_financial_cycle(req: FinancialCycleRequest):
    audit_log("finance_calculation_requested", {"module": "financial_cycle", "scope": req.scope, "source": req.source})
    result = calculate_financial_cycle(
        average_inventory_days=req.average_inventory_days,
        average_receivable_days=req.average_receivable_days,
        average_payable_days=req.average_payable_days,
        source=req.source,
        scope=req.scope,
    )
    audit_log("finance_calculation_completed", {"module": "financial_cycle", "success": result["success"], "warnings": result["warnings"]})
    return safe_response(result)


@app.post("/tokyo/finance/calculate/minimum-cash")
async def finance_calculate_minimum_cash(req: MinimumCashRequest):
    audit_log("finance_calculation_requested", {"module": "minimum_cash", "scope": req.scope, "source": req.source})
    result = calculate_minimum_cash(
        daily_cash_need=req.daily_cash_need,
        financial_cycle_days=req.financial_cycle_days,
        safety_days=req.safety_days,
        source=req.source,
        scope=req.scope,
    )
    audit_log("finance_calculation_completed", {"module": "minimum_cash", "success": result["success"], "warnings": result["warnings"]})
    return safe_response(result)


# ═══════════════════════════════════════════════════════════
# PHASE 2: SPREADSHEET UPLOAD CENTER
# ═══════════════════════════════════════════════════════════

UPLOAD_DIR = Path(os.getenv("TOKYO_DATA_DIR", "/opt/tokyo/Tokyo painel/data")) / "uploads" / "finance"
IMPORT_DIR = Path(os.getenv("TOKYO_DATA_DIR", "/opt/tokyo/Tokyo painel/data")) / "imported" / "finance"


@app.get("/tokyo/finance/uploads/status")
async def finance_uploads_status():
    return safe_response({
        "upload_center": "Bunny Intelligence Bank > Planilhas Financeiras",
        "status": "planned",
        "upload_enabled": False,
        "reason": "upload_parser_pending",
        "rules": {
            "never_overwrite_original": True,
            "save_copy_with_timestamp": True,
            "register_metadata": True,
            "no_macro_execution": True,
            "no_formula_trust_without_validation": True,
            "accepted_formats": [".xlsx", ".csv"],
            "blocked_formats": [".xlsm", ".exe", ".zip", ".sh", ".py"],
        },
        "directories": {
            "uploads": str(UPLOAD_DIR),
            "imported": str(IMPORT_DIR),
        },
        "token_exposed": False,
    })


@app.get("/tokyo/finance/uploads/registry")
async def finance_uploads_registry():
    imports = []
    if IMPORT_DIR.exists():
        for f in sorted(IMPORT_DIR.glob("*.json")):
            try:
                imports.append(json.loads(f.read_text()))
            except Exception:
                pass
    return safe_response({
        "imports": imports,
        "count": len(imports),
        "status": "planned",
        "message": "Upload center prepared. Nenhum arquivo importado ainda.",
        "token_exposed": False,
    })


class UploadValidateRequest(BaseModel):
    filename: str
    file_size: Optional[int] = None


@app.post("/tokyo/finance/uploads/validate")
async def finance_uploads_validate(req: UploadValidateRequest):
    filename = req.filename.lower()
    blocked = [".xlsm", ".exe", ".zip", ".sh", ".py", ".bat", ".cmd", ".ps1"]
    blocked_reason = None
    for ext in blocked:
        if filename.endswith(ext):
            blocked_reason = f"Formato bloqueado: {ext}. Macros/executaveis nao sao aceitos."
            break

    accepted = [".xlsx", ".csv"]
    accepted_ext = any(filename.endswith(ext) for ext in accepted)

    audit_log("spreadsheet_validated" if accepted_ext else "spreadsheet_blocked", {
        "filename": filename,
        "accepted": accepted_ext,
        "blocked_reason": blocked_reason,
    })

    return safe_response({
        "valid": accepted_ext and not blocked_reason,
        "filename": req.filename,
        "accepted": accepted_ext,
        "blocked_reason": blocked_reason,
        "message": "Arquivo valido para upload futuro." if accepted_ext and not blocked_reason else ("Arquivo bloqueado: " + blocked_reason),
    })


# ═══════════════════════════════════════════════════════════
# PHASE 2: BUSINESS DATA LAYER
# ═══════════════════════════════════════════════════════════

SCOPES = [
    {"id": "grupsbunny", "name": "GrupsBunny", "type": "holding", "status": "active", "data_source": "pending_api", "validation_status": "pending_validation"},
    {"id": "bunny_dreams", "name": "Bunny Dreams", "type": "retail", "status": "active", "data_source": "pending_api", "validation_status": "pending_validation"},
    {"id": "riverside", "name": "Loja Riverside", "type": "store", "status": "active", "data_source": "pending_api", "validation_status": "pending_validation"},
    {"id": "teresina", "name": "Loja Teresina", "type": "store", "status": "active", "data_source": "pending_api", "validation_status": "pending_validation"},
    {"id": "bunny_siberian", "name": "Bunny Siberian", "type": "systems_company", "status": "active", "data_source": "pending_api", "validation_status": "pending_validation"},
    {"id": "sistema_siberian", "name": "Sistema Siberian ERP", "type": "product", "status": "planned", "data_source": "pending_api", "validation_status": "pending_validation"},
]

DATA_SOURCES = [
    {"id": "pending_api", "type": "api", "status": "not_configured", "mode": "read_only", "description": "Sistema Siberian API — nao configurada"},
    {"id": "manual_input", "type": "manual", "status": "available", "mode": "read_only", "description": "Entrada manual de dados (pending_validation)"},
    {"id": "spreadsheet_upload", "type": "file", "status": "planned", "mode": "read_only", "description": "Upload de planilhas (futuro)"},
    {"id": "spreadsheet_reference", "type": "file", "status": "recognized", "mode": "reference_only", "description": "Planilhas de referencia (modelos estruturais)"},
]


@app.get("/tokyo/business/data-sources")
async def business_data_sources():
    return safe_response({
        "data_sources": DATA_SOURCES,
        "active_sources": [ds for ds in DATA_SOURCES if ds["status"] in ("available", "active")],
        "token_exposed": False,
    })


@app.get("/tokyo/business/scopes")
async def business_scopes():
    return safe_response({
        "scopes": SCOPES,
        "count": len(SCOPES),
        "token_exposed": False,
    })


@app.get("/tokyo/business/readiness")
async def business_readiness():
    ready = any(s["data_source"] not in ("pending_api", "not_configured") for s in SCOPES)
    return safe_response({
        "ready": ready,
        "status": "pending_data" if not ready else "data_available",
        "message": "Dados empresariais ainda nao conectados. Configure Sistema Siberian API ou importe planilhas autorizadas." if not ready else "Alguns dados empresariais disponiveis.",
        "scopes_summary": {s["id"]: {"data_source": s["data_source"], "validation_status": s["validation_status"]} for s in SCOPES},
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 2: AUDIT LOG ENDPOINT
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/finance/audit")
async def finance_audit_log():
    from finance_engine.audit import AUDIT_FILE
    entries = []
    if AUDIT_FILE.exists():
        try:
            for line in AUDIT_FILE.read_text().strip().split("\n"):
                if line:
                    entries.append(json.loads(line))
        except Exception:
            pass
    return safe_response({
        "audit_log": "phase_2_finance_data_layer.jsonl",
        "entries": entries[-50:],
        "total": len(entries),
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3B: VOICE CONTROL CENTER
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/voice/capabilities")
async def voice_capabilities():
    return safe_response({
        "provider": "LiveKit + Google Gemini Realtime",
        "voice_name": "Charon",
        "capabilities": ["realtime_conversation", "memory", "noise_cancellation", "video"],
        "activation_modes": {
            "push_to_talk": "planned",
            "wake_word": {"status": "planned", "word": "Tokyo"},
            "continuous": "planned",
            "command_preview": "active",
        },
        "configured": env_present("LIVEKIT_URL"),
        "token_exposed": False,
    })


@app.get("/tokyo/voice/activation/status")
async def voice_activation_status():
    return safe_response({
        "activation": {
            "mode": "push_to_talk_planned",
            "wake_word": "Tokyo",
            "wake_word_status": "planned",
            "commands_executable": False,
            "reason": "Voice commands are preview-only in this phase. No real actions executed.",
        },
        "commands_available": 8,
        "commands": [
            {"command": "Tokyo, abrir dashboard", "target": "/ui", "status": "planned"},
            {"command": "Tokyo, abrir MCP", "target": "/ui#mcp", "status": "planned"},
            {"command": "Tokyo, abrir financeiro", "target": "/ui#finance", "status": "planned"},
            {"command": "Tokyo, status do sistema", "target": "/tokyo/system/health", "status": "planned"},
            {"command": "Tokyo, abrir API Hub", "target": "/ui#api-hub", "status": "planned"},
        ],
        "token_exposed": False,
    })


class VoicePreviewRequest(BaseModel):
    command: str

@app.post("/tokyo/voice/activation/preview")
async def voice_activation_preview(req: VoicePreviewRequest):
    available_commands = [
        {"command": "Tokyo, abrir dashboard", "target": "/ui"},
        {"command": "Tokyo, abrir MCP", "target": "/ui#mcp"},
        {"command": "Tokyo, abrir financeiro", "target": "/ui#finance"},
        {"command": "Tokyo, abrir setup", "target": "/setup"},
        {"command": "Tokyo, status do sistema", "target": "/tokyo/system/health"},
        {"command": "Tokyo, abrir API Hub", "target": "/ui#api-hub"},
        {"command": "Tokyo, mostrar Bunny Dreams", "target": "/ui#bunny-dreams"},
        {"command": "Tokyo, abrir voz", "target": "/ui#voice"},
    ]
    matched = [c for c in available_commands if c["command"] == req.command]
    if matched:
        target = matched[0]["target"]
        return safe_response({
            "recognized": True,
            "command": req.command,
            "target": target,
            "action": "preview_only",
            "executed": False,
            "message": f"Command '{req.command}' recognized. Preview only - no action executed.",
        })
    available_str = ", ".join([c["command"] for c in available_commands])
    return safe_response({
        "recognized": False,
        "command": req.command,
        "action": "preview_only",
        "executed": False,
        "message": f"Command not recognized. Available: {available_str}",
    })


@app.post("/tokyo/voice/activation/test-command")
async def voice_test_command(req: VoicePreviewRequest):
    return await voice_activation_preview(req)


@app.get("/tokyo/voice/interface/status")
async def voice_interface_status():
    return safe_response({
        "voice_provider": "livekit_gemini_realtime",
        "voice_name": "Charon",
        "session_state": "idle",
        "states_available": ["offline", "idle", "listening", "thinking", "speaking", "error"],
        "mic_available": None,
        "push_to_talk": "planned",
        "wake_word": "planned",
        "activation_preview_enabled": True,
        "live_execution_enabled": False,
        "safety_mode": True,
        "configured": env_present("LIVEKIT_URL"),
        "visualizer_modes": ["orb", "wave_bars", "radial", "aura"],
        "current_visualizer": "orb",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/session/mock-status")
async def voice_session_mock_status():
    return safe_response({
        "session": {
            "active": False,
            "state": "idle",
            "last_user_transcript": None,
            "last_assistant_response": None,
            "transcript_history": [],
            "duration_seconds": 0,
        },
        "mode": "mock_preview",
        "message": "Sessao real nao iniciada. Preview mode only. Configure LiveKit para sessao real.",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3B: MCP PANEL
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/mcp/servers")
async def mcp_servers():
    config = load_json_config("mcp_servers.example.json")
    if config:
        return safe_response(config)
    return safe_response({
        "mcp_servers": [],
        "mode": "optional",
        "required": False,
        "token_exposed": False,
    })


@app.get("/tokyo/mcp/capabilities")
async def mcp_capabilities():
    return safe_response({
        "mcp": {
            "enabled": env_bool("MCP_ENABLED"),
            "required": False,
            "status": "configured" if env_present("MCP_BASE_URL") else "not_configured",
            "mode": "optional",
            "safe_mode": True,
            "capabilities": ["tools", "context", "servers"],
            "servers_registered": 5,
            "servers_active": 0,
        },
        "token_exposed": False,
    })


@app.get("/tokyo/mcp/tools")
async def mcp_tools():
    return safe_response({
        "tools": [],
        "status": "not_configured",
        "message": "MCP nao configurado. Ferramentas indisponiveis.",
        "token_exposed": False,
    })


class MCPTestRequest(BaseModel):
    server_id: Optional[str] = None
    base_url: Optional[str] = None

@app.post("/tokyo/mcp/test-connection")
async def mcp_test_connection(req: MCPTestRequest):
    return safe_response({
        "tested": False,
        "reason": "MCP test-connection is a preview placeholder. Configure MCP_BASE_URL in .env to enable.",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3B: API HUB / EXTERNAL TOOLS
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/api-hub/connectors")
async def api_hub_connectors():
    config = load_json_config("external_tools.example.json")
    if config:
        return safe_response(config)
    return safe_response({"external_tools": [], "token_exposed": False})


@app.get("/tokyo/api-hub/tools")
async def api_hub_tools():
    config = load_json_config("external_tools.example.json")
    if config:
        tools_summary = [
            {"id": t["id"], "name": t["name"], "status": t["status"], "required": t["required"], "mode": t["mode"], "safe_mode": t["safe_mode"]}
            for t in config.get("external_tools", [])
        ]
        return safe_response({"tools": tools_summary, "total": len(tools_summary), "all_required_false": True, "token_exposed": False})
    return safe_response({"tools": [], "token_exposed": False})


@app.get("/tokyo/api-hub/readiness")
async def api_hub_readiness():
    return safe_response({
        "ready": False,
        "status": "not_configured",
        "message": "API Hub configurado. Ferramentas externas planejadas mas nao instaladas. Conecte ferramentas via ZimaOS/Docker quando disponivel.",
        "external_write_enabled": False,
        "token_exposed": False,
    })


class APITestRequest(BaseModel):
    connector_id: str

@app.post("/tokyo/api-hub/test-connector")
async def api_hub_test_connector(req: APITestRequest):
    return safe_response({
        "tested": False,
        "connector_id": req.connector_id,
        "reason": f"Teste de conector '{req.connector_id}' e um placeholder. Configure as variaveis de ambiente correspondentes para ativar.",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3B: ZIMAOS READY CENTER
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/zimaos/status")
async def zimaos_status():
    import shutil
    docker_installed = shutil.which("docker") is not None
    compose_file = BASE_DIR / "docker-compose.yml"
    dockerfile = BASE_DIR / "Dockerfile"
    return safe_response({
        "zimaos": {
            "app_port": 8788,
            "data_path": "/DATA/AppData/tokyoos",
            "volume": "/DATA/AppData/tokyoos:/data/tokyo",
            "network_mode": "bridge",
            "restart": "unless-stopped",
            "store_app_id": "tokyoos",
            "scheme": "http",
            "index": "/ui",
            "x_casaos": True,
        },
        "docker": {
            "installed": docker_installed,
            "compose_file_exists": compose_file.exists(),
            "dockerfile_exists": dockerfile.exists(),
            "healthcheck": True,
        },
        "token_exposed": False,
    })


@app.get("/tokyo/zimaos/readiness")
async def zimaos_readiness():
    import shutil
    docker_installed = shutil.which("docker") is not None
    compose_file = BASE_DIR / "docker-compose.yml"
    issues = []
    if not docker_installed:
        issues.append("Docker not installed on this host")
    if not compose_file.exists():
        issues.append("docker-compose.yml not found")
    return safe_response({
        "ready": docker_installed and compose_file.exists(),
        "docker_installed": docker_installed,
        "compose_exists": compose_file.exists(),
        "issues": issues,
        "next_step": "docker compose up -d" if docker_installed and compose_file.exists() else "Install Docker and ensure docker-compose.yml is present",
        "token_exposed": False,
    })


@app.get("/tokyo/zimaos/docker-status")
async def zimaos_docker_status():
    import shutil
    docker_installed = shutil.which("docker") is not None
    return safe_response({
        "docker_installed": docker_installed,
        "docker_compose_available": (BASE_DIR / "docker-compose.yml").exists(),
        "dockerfile_available": (BASE_DIR / "Dockerfile").exists(),
        "healthcheck_configured": True,
        "token_exposed": False,
    })


@app.get("/tokyo/zimaos/install-checklist")
async def zimaos_install_checklist():
    return safe_response({
        "checklist": [
            {"step": "app.py running", "status": "done", "detail": "FastAPI backend active"},
            {"step": "Dockerfile", "status": "done" if (BASE_DIR / "Dockerfile").exists() else "pending", "detail": "Container build definition"},
            {"step": "docker-compose.yml", "status": "done" if (BASE_DIR / "docker-compose.yml").exists() else "pending", "detail": "Orchestration + x-casaos labels"},
            {"step": "x-casaos labels", "status": "done", "detail": "ZimaOS app store metadata"},
            {"step": "Healthcheck", "status": "done", "detail": "/tokyo/system/health"},
            {"step": "Data volumes", "status": "done", "detail": "/DATA/AppData/tokyoos:/data/tokyo"},
            {"step": "External tools planned", "status": "done", "detail": "Hermes, MCP, Ollama, OpenWebUI, etc."},
            {"step": "Environment file", "status": "done" if env_present("TOKYO_ENV") else "pending", "detail": ".env configuration"},
        ],
        "ready": True,
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3B: INSTALL MODE (SETUP PAGE)
# ═══════════════════════════════════════════════════════════

@app.get("/setup", response_class=HTMLResponse)
async def serve_setup():
    ui_file = INTERFACE_DIR / "index.html"
    if ui_file.exists():
        content = ui_file.read_text(encoding="utf-8")
        # Inject script to activate setup page automatically
        content = content.replace('</body>', '<script>setTimeout(() => { document.getElementById("page-setup") && switchMode("install"); }, 500);</script></body>')
        return HTMLResponse(content=content)
    return HTMLResponse(content="<h1>TokyoOS Setup</h1>", status_code=404)

class EnvUpdateRequest(BaseModel):
    env_vars: dict[str, str]

@app.get("/tokyo/system/env")
async def system_env():
    env_file = BASE_DIR / ".env"
    public_keys = [
        "GEMINI_MODEL", "OPENAI_MODEL", "TOKYO_DEFAULT_LLM_PROVIDER", 
        "LIVEKIT_URL", "HERMES_BASE_URL", "OPENCLAW_BASE_URL", "OLLAMA_BASE_URL",
        "BROWSER_USE_BASE_URL", "FIRECRAWL_BASE_URL", "OBSIDIAN_BASE_URL", "N8N_BASE_URL",
        "OLLAMA_MODEL", "GLOBAL_LOCAL_LLM_PROVIDER"
    ]
    secret_keys = [
        "GEMINI_API_KEY", "OPENAI_API_KEY", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "MEM0_API_KEY", "TELEGRAM_BOT_TOKEN", "APPLE_AGENT_API_KEY", "WHATSAPP_API_TOKEN",
        "SIBERIAN_API_KEY", "BUNNY_SIBERIAN_API_KEY", "GMAIL_API_KEY", "GOOGLE_DRIVE_API_KEY",
        "ICLOUD_API_KEY", "INSTAGRAM_API_KEY", "TIKTOK_API_KEY", "OPENCODE_API_KEY"
    ]
    current = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                if k in public_keys:
                    current[k] = v
                elif k in secret_keys:
                    current[k] = "configured" if v else ""
    return safe_response({"env": current, "token_exposed": False})

@app.post("/tokyo/system/env/update")
async def system_env_update(req: EnvUpdateRequest):
    env_file = BASE_DIR / ".env"
    lines = []
    if env_file.exists():
        lines = env_file.read_text().splitlines()
    
    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            k, v = line.split("=", 1)
            k = k.strip()
            if k in req.env_vars:
                new_val = req.env_vars[k]
                if new_val and new_val != "configured":
                    new_lines.append(f"{k}={new_val}")
                    os.environ[k] = new_val
                else:
                    new_lines.append(line)
                updated_keys.add(k)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    for k, v in req.env_vars.items():
        if k not in updated_keys and v and v != "configured":
            new_lines.append(f"{k}={v}")
            os.environ[k] = v
            
    env_file.write_text("\n".join(new_lines) + "\n")
    return safe_response({"updated": True, "token_exposed": False})

@app.get("/tokyo/system/health/integrations")
async def system_health_integrations():
    env_file = BASE_DIR / ".env"
    current = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                current[k.strip()] = v.strip().strip("'").strip('"')
    
    status_map = {}
    
    # Helthcheck URL configurations
    # We use a short timeout because if it's down, we don't want the UI to hang.
    async def check_url(url: str, is_ollama: bool = False) -> str:
        if not url: return "pending"
        # Cleanup trailing slashes
        url = url.rstrip('/')
        try:
            test_url = f"{url}/api/version" if is_ollama else url
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(test_url)
                if res.status_code < 500: # 404 is fine for base URLs if no auth, 401 is also fine, it means it's alive!
                    return "connected"
                return "error"
        except Exception as e:
            return "error"

    # API Keys are just marked as configured for now unless we implement specific pings for each cloud provider
    def check_key(key: str) -> str:
        if current.get(key): return "connected"
        return "pending"

    # Nuvem / Cloud
    status_map["GEMINI_API_KEY"] = check_key("GEMINI_API_KEY")
    status_map["OPENAI_API_KEY"] = check_key("OPENAI_API_KEY")
    status_map["LIVEKIT_URL"] = check_key("LIVEKIT_URL") # Just check if exists, livekit needs secret to ping
    
    # Ferramentas Locais (Active Pings)
    status_map["OLLAMA_BASE_URL"] = await check_url(current.get("OLLAMA_BASE_URL"), is_ollama=True)
    status_map["HERMES_BASE_URL"] = await check_url(current.get("HERMES_BASE_URL"))
    status_map["N8N_BASE_URL"] = await check_url(current.get("N8N_BASE_URL"))
    status_map["BROWSER_USE_BASE_URL"] = await check_url(current.get("BROWSER_USE_BASE_URL"))
    status_map["OPENCLAW_BASE_URL"] = await check_url(current.get("OPENCLAW_BASE_URL"))
    
    # External APIs
    status_map["MEM0_API_KEY"] = check_key("MEM0_API_KEY")
    status_map["FIRECRAWL_BASE_URL"] = check_key("FIRECRAWL_BASE_URL")
    status_map["TELEGRAM_BOT_TOKEN"] = check_key("TELEGRAM_BOT_TOKEN")
    
    return safe_response({"statuses": status_map})


# ═══════════════════════════════════════════════════════════
# PHASE 3C: ZIMAOS DEPLOY READINESS (extended)
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/zimaos/volumes")
async def zimaos_volumes():
    return safe_response({
        "volumes": [
            {"host": "/DATA/AppData/tokyoos", "container": "/data/tokyo", "mode": "rw", "status": "configured"},
            {"container": "/data/tokyo/tools", "host": "/DATA/AppData/tokyoos/tools", "status": "planned"},
            {"container": "/data/tokyo/connectors", "host": "/DATA/AppData/tokyoos/connectors", "status": "planned"},
            {"container": "/data/tokyo/mcp", "host": "/DATA/AppData/tokyoos/mcp", "status": "planned"},
            {"container": "/data/tokyo/logs", "host": "/DATA/AppData/tokyoos/logs", "status": "configured"},
            {"container": "/data/tokyo/uploads", "host": "/DATA/AppData/tokyoos/uploads", "status": "planned"},
            {"container": "/data/tokyo/cache", "host": "/DATA/AppData/tokyoos/cache", "status": "planned"},
            {"container": "/data/tokyo/config", "host": "/DATA/AppData/tokyoos/config", "status": "planned"},
        ],
        "token_exposed": False,
    })


@app.get("/tokyo/zimaos/ports")
async def zimaos_ports():
    return safe_response({
        "ports": [
            {"container": 8788, "host": 8788, "protocol": "tcp", "description": "TokyoOS HTTP API + UI"},
        ],
        "external_tools_planned_ports": {
            "hermes": 8791, "mcp": 8789, "ollama": 11434, "openwebui": 3000, "n8n": 5678,
        },
        "token_exposed": False,
    })


@app.get("/tokyo/zimaos/app-metadata")
async def zimaos_app_metadata():
    return safe_response({
        "app": {
            "title": "TokyoOS",
            "developer": "GrupsBunny",
            "author": "GrupsBunny",
            "category": "Utilities",
            "tagline": "Tokyo IA — GrupsBunny AI Hub with Voice, Dashboard & ERP",
            "description": "Assistente de IA com voz, dashboard empresarial, integracao ERP, MCP opcional e preparacao para ferramentas externas no ZimaOS.",
            "version": "3.2.0-phase3c",
            "store_app_id": "tokyoos",
            "scheme": "http",
            "port_map": "8788",
            "index": "/ui",
            "icon": "placeholder",
        },
        "docker": {
            "image": "tokyoos:latest",
            "build": "Dockerfile",
            "restart": "unless-stopped",
            "volumes": ["/DATA/AppData/tokyoos:/data/tokyo"],
            "ports": ["8788:8788"],
            "healthcheck": "/tokyo/system/health",
        },
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3C: TOOLS DIRECTORY MODEL
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/tools/directories")
async def tools_directories():
    data_dir = Path(os.getenv("TOKYO_DATA_DIR", "/data/tokyo"))
    dirs = ["tools", "connectors", "mcp", "logs", "uploads", "cache", "config", "releases"]
    result = {}
    for d in dirs:
        p = data_dir / d
        result[d] = {"path": str(p), "exists": p.exists()}
    return safe_response({
        "data_dir": str(data_dir),
        "directories": result,
        "all_exist": all(v["exists"] for v in result.values()),
        "mode": "planned",
        "message": "Diretorios criados conforme disponivel. Alguns podem ser criados no primeiro deploy.",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3C: EXTERNAL TOOLS ENV CHECKLIST
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/tools/env-checklist")
async def tools_env_checklist():
    tools = [
        {"id": "hermes", "env": ["HERMES_ENABLED=false", "HERMES_BASE_URL=", "HERMES_API_KEY="], "port": 8791, "required": False},
        {"id": "mcp", "env": ["MCP_ENABLED=false", "MCP_BASE_URL=", "MCP_API_KEY="], "port": 8789, "required": False},
        {"id": "ollama", "env": ["OLLAMA_ENABLED=false", "OLLAMA_BASE_URL=http://host.docker.internal:11434"], "port": 11434, "required": False},
        {"id": "openwebui", "env": ["OPENWEBUI_ENABLED=false", "OPENWEBUI_BASE_URL=", "OPENWEBUI_API_KEY="], "port": 3000, "required": False},
        {"id": "browser_use", "env": ["BROWSER_USE_ENABLED=false", "BROWSER_USE_BASE_URL=", "BROWSER_USE_API_KEY="], "required": False},
        {"id": "firecrawl", "env": ["FIRECRAWL_ENABLED=false", "FIRECRAWL_BASE_URL=", "FIRECRAWL_API_KEY="], "required": False},
        {"id": "n8n", "env": ["N8N_ENABLED=false", "N8N_BASE_URL=", "N8N_API_KEY="], "port": 5678, "required": False},
        {"id": "openclaw", "env": ["OPENCLAW_ENABLED=false", "OPENCLAW_BASE_URL=", "OPENCLAW_API_KEY="], "required": False},
        {"id": "apple_agent", "env": ["APPLE_AGENT_ENABLED=false", "APPLE_AGENT_BASE_URL=", "APPLE_AGENT_API_KEY="], "required": False, "status": "planned"},
        {"id": "telegram", "env": ["TELEGRAM_ENABLED=false", "TELEGRAM_BOT_TOKEN="], "required": False},
        {"id": "whatsapp", "env": ["WHATSAPP_ENABLED=false", "WHATSAPP_API_URL=", "WHATSAPP_API_TOKEN="], "required": False},
    ]
    return safe_response({"tools": tools, "total": len(tools), "auto_install_enabled": False, "token_exposed": False})


# ═══════════════════════════════════════════════════════════
# PHASE 3E: VOICE SPEECH DIAGNOSTIC
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/voice/speech/status")
async def voice_speech_status():
    livekit_ready = env_present("LIVEKIT_URL") and env_present("LIVEKIT_API_KEY") and env_present("LIVEKIT_API_SECRET")
    gemini_ready = env_present("GEMINI_API_KEY") or env_present("GOOGLE_API_KEY")
    return safe_response({
        "speech": {
            "enabled": livekit_ready and gemini_ready,
            "provider": "LiveKit + Gemini Realtime",
            "livekit_configured": livekit_ready,
            "gemini_realtime_configured": gemini_ready,
            "tts_available": livekit_ready,
            "last_voice_error": None,
            "session_state": "idle",
            "voice_name": "Charon",
        },
        "browser_requirements": {
            "autoplay_possible": True,
            "requires_user_gesture": True,
            "recommendation": "Clique em 'Iniciar Sessao' para ativar o audio do navegador.",
        },
        "message": "Fala disponivel se LiveKit e Gemini estiverem configurados. Clique em Iniciar Sessao." if livekit_ready and gemini_ready else "Fala nao configurada. Configure LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET e GEMINI_API_KEY no .env.",
        "token_exposed": False,
    })


class SpeechTestRequest(BaseModel):
    text: str = "Tokyo online. Sistema de voz pronto."

@app.post("/tokyo/voice/speech/test")
async def voice_speech_test(req: SpeechTestRequest):
    livekit_ready = env_present("LIVEKIT_URL") and env_present("LIVEKIT_API_KEY")
    return safe_response({
        "requested_text": req.text,
        "configured": livekit_ready,
        "status": "not_configured" if not livekit_ready else "configured_but_not_triggered",
        "message": "TTS backend configurado mas teste real requer sessao LiveKit ativa." if livekit_ready else "TTS nao configurado. Configure LiveKit no .env.",
        "action": "preview_only",
        "executed": False,
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3E: VISION / CAMERA
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/vision/status")
async def vision_status():
    return safe_response({
        "vision": {
            "enabled": False,
            "camera_preview_available": None,
            "livekit_video_enabled": False,
            "gemini_vision_enabled": False,
            "mode": "preview_only",
            "privacy": {
                "auto_recording": False,
                "auto_frame_upload": False,
                "requires_user_action": True,
                "never_saves_frames_automatically": True,
            },
        },
        "message": "Camera/visao em modo preview. Ative manualmente no painel de voz.",
        "token_exposed": False,
    })


@app.get("/tokyo/vision/capabilities")
async def vision_capabilities():
    return safe_response({
        "capabilities": [
            {"id": "camera_preview", "status": "planned", "requires_browser_permission": True},
            {"id": "livekit_video_track", "status": "planned", "requires_livekit": True},
            {"id": "gemini_vision_frame", "status": "planned", "requires_gemini": True},
            {"id": "describe_scene", "status": "planned", "mode": "preview_only"},
        ],
        "token_exposed": False,
    })


@app.get("/tokyo/vision/livekit/status")
async def vision_livekit_status():
    return safe_response({
        "livekit_video": {
            "enabled": env_present("LIVEKIT_URL"),
            "video_track_supported": True,
            "simulcast_supported": True,
            "mode": "preview_only",
        },
        "token_exposed": False,
    })


class VisionDescribeRequest(BaseModel):
    description: Optional[str] = None

@app.post("/tokyo/vision/preview/describe")
async def vision_preview_describe(req: VisionDescribeRequest):
    return safe_response({
        "described": req.description is not None,
        "input": req.description,
        "status": "preview_only",
        "message": "Visao real nao configurada. Preview apenas recebe texto, nao processa imagem.",
        "action": "preview_only",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 3E: STORE DASHBOARDS — KPIs
# ═══════════════════════════════════════════════════════════

VALID_STORES = {"riverside", "teresina"}

def store_pending_response(store_id, module):
    return {
        "success": True,
        "store_id": store_id,
        "module": module,
        "status": "pending_api",
        "data": None,
        "source": "pending_api",
        "message": f"Dados de {module} da loja {store_id} ainda nao conectados. Configure Sistema Siberian API ou importe planilhas.",
        "token_exposed": False,
    }

def store_kpi_template(store_id, kpis):
    return {
        "success": True,
        "store_id": store_id,
        "status": "pending_api",
        "source": "pending_api",
        "kpis": [{**k, "value": None, "status": "pending_api"} for k in kpis],
        "message": f"KPIs da loja {store_id}. Dados reais pendentes de API.",
        "token_exposed": False,
    }


@app.get("/tokyo/stores/{store_id}/sales/kpis")
async def store_sales_kpis(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store", "valid": list(VALID_STORES)}, 400)
    return safe_response(store_kpi_template(store_id, [
        {"id": "meta_mes", "label": "Meta Mes", "type": "currency", "source": "manual_input"},
        {"id": "meta_dia", "label": "Meta Dia", "type": "currency", "source": "calculated_pending"},
        {"id": "meta_dia_gap", "label": "Meta Dia com GAP", "type": "currency", "source": "calculated_pending"},
        {"id": "gap", "label": "GAP (meta - vendido)", "type": "currency", "source": "pending_api"},
        {"id": "faturamento_anterior", "label": "Faturamento Dia Anterior", "type": "currency", "source": "pending_api"},
        {"id": "faturamento_realtime", "label": "Faturamento Tempo Real", "type": "currency", "source": "pending_api"},
        {"id": "tendencia", "label": "Tendencia Fechamento", "type": "currency", "source": "calculated_pending"},
        {"id": "crescimento_semanal", "label": "Crescimento Semana vs Semana", "type": "percentage", "source": "pending_api"},
        {"id": "ticket_medio", "label": "Ticket Medio", "type": "currency", "source": "pending_api"},
    ]))


@app.get("/tokyo/stores/{store_id}/sales/trend-calendar")
async def store_sales_trend_calendar(store_id: str, month: str = "2026-06"):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response({
        "success": True, "store_id": store_id, "month": month,
        "status": "pending_api", "days": [], "source": "pending_api",
        "token_exposed": False,
    })


@app.get("/tokyo/stores/{store_id}/sales/sellers")
async def store_sales_sellers(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "sellers"))


@app.get("/tokyo/stores/{store_id}/finance/kpis")
async def store_finance_kpis(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_kpi_template(store_id, [
        {"id": "dre_receita", "label": "Receita (DRE)", "type": "currency"},
        {"id": "dre_custos", "label": "Custos", "type": "currency"},
        {"id": "dre_lucro", "label": "Lucro/Prejuizo", "type": "currency"},
        {"id": "cashflow_entradas", "label": "Entradas Caixa", "type": "currency"},
        {"id": "cashflow_saidas", "label": "Saidas Caixa", "type": "currency"},
        {"id": "cashflow_saldo", "label": "Saldo", "type": "currency"},
        {"id": "lucro_operacional", "label": "Lucro Operacional", "type": "currency"},
        {"id": "margem", "label": "Margem", "type": "percentage"},
        {"id": "break_even", "label": "Ponto de Equilibrio", "type": "currency"},
    ]))


@app.get("/tokyo/stores/{store_id}/finance/dre")
async def store_finance_dre(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "dre"))


@app.get("/tokyo/stores/{store_id}/finance/cash-flow")
async def store_finance_cash_flow(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "cash_flow"))


@app.get("/tokyo/stores/{store_id}/finance/break-even")
async def store_finance_break_even(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "break_even"))


@app.get("/tokyo/stores/{store_id}/stock/kpis")
async def store_stock_kpis(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_kpi_template(store_id, [
        {"id": "dead_stock_30d", "label": "Parado >30 dias", "type": "count"},
        {"id": "top_sellers_week", "label": "Mais Vendidos Semana", "type": "list"},
        {"id": "zero_stock", "label": "Estoque Zerado", "type": "count"},
        {"id": "critical_stock", "label": "Estoque Critico", "type": "count"},
        {"id": "losses", "label": "Perdas/Avarias", "type": "currency"},
        {"id": "ruptura_estimada", "label": "Ruptura Estimada", "type": "currency"},
    ]))


@app.get("/tokyo/stores/{store_id}/stock/dead-stock")
async def store_stock_dead(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "dead_stock"))


@app.get("/tokyo/stores/{store_id}/stock/top-sellers-week")
async def store_stock_top(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "top_sellers"))


@app.get("/tokyo/stores/{store_id}/stock/zero-stock")
async def store_stock_zero(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "zero_stock"))


@app.get("/tokyo/stores/{store_id}/stock/critical-stock")
async def store_stock_critical(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "critical_stock"))


@app.get("/tokyo/stores/{store_id}/stock/losses")
async def store_stock_losses(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response(store_pending_response(store_id, "losses"))


@app.get("/tokyo/stores/targets/status")
async def stores_targets_status():
    return safe_response({
        "targets": {"riverside": [], "teresina": []},
        "status": "planned",
        "editable": False,
        "message": "Metas mensais planejadas. Configure via API ou manual futuramente.",
        "token_exposed": False,
    })


@app.get("/tokyo/stores/{store_id}/targets")
async def store_targets(store_id: str):
    if store_id not in VALID_STORES: return JSONResponse({"error": "invalid store"}, 400)
    return safe_response({
        "store_id": store_id, "targets": [], "status": "planned",
        "message": f"Metas da loja {store_id} ainda nao definidas.",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 4A: LIVEKIT REAL SESSION
# ═══════════════════════════════════════════════════════════

import uuid
import time

def _livekit_ready():
    return bool(env_present("LIVEKIT_URL") and env_present("LIVEKIT_API_KEY") and env_present("LIVEKIT_API_SECRET"))

def _gemini_ready():
    return bool(env_present("GEMINI_API_KEY") or env_present("GOOGLE_API_KEY"))

def _generate_livekit_token(room_name=None, identity="tokyo-user"):
    if not _livekit_ready():
        return None
    try:
        from livekit import api
        token = api.AccessToken(
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
        )
        token.with_identity(identity)
        token.with_name(identity)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name or f"tokyo-voice-{uuid.uuid4().hex[:8]}",
        ))
        return token.to_jwt()
    except Exception as e:
        logger.warning(f"LiveKit token generation failed: {e}")
        return None


@app.get("/tokyo/voice/livekit/status")
async def voice_livekit_status():
    ready = _livekit_ready()
    return safe_response({
        "livekit": {
            "configured": ready,
            "url_configured": env_present("LIVEKIT_URL"),
            "api_key_configured": env_present("LIVEKIT_API_KEY"),
            "api_secret_configured": env_present("LIVEKIT_API_SECRET"),
            "can_issue_token": True if ready else False,
            "audio_ready": ready,
            "video_ready": ready,
            "room_creation_mode": "auto_generated",
        },
        "message": "LiveKit pronto para sessao." if ready else "LiveKit nao configurado. Configure LIVEKIT_URL, LIVEKIT_API_KEY e LIVEKIT_API_SECRET.",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/gemini-realtime/status")
async def voice_gemini_realtime_status():
    ready = _gemini_ready()
    return safe_response({
        "gemini_realtime": {
            "configured": ready,
            "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            "audio_input_supported": ready,
            "audio_output_supported": ready,
            "voice_name": "Charon",
            "last_error": None,
        },
        "message": "Gemini Realtime pronto para voz." if ready else "Gemini Realtime nao configurado. Configure GEMINI_API_KEY.",
        "token_exposed": False,
    })


@app.post("/tokyo/voice/gemini-realtime/handshake-test")
async def voice_gemini_handshake_test():
    ready = _gemini_ready()
    return safe_response({
        "handshake": {
            "attempted": False,
            "configured": ready,
            "status": "configured_ready" if ready else "not_configured",
        },
        "next_step": "Inicie uma sessao LiveKit. O handshake Gemini Realtime ocorre automaticamente dentro da sessao." if ready else "Configure GEMINI_API_KEY no .env.",
        "message": "Gemini Realtime handshake integrado na sessao LiveKit. Nao requer acao separada.",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/session/status")
async def voice_session_status():
    ready = _livekit_ready() and _gemini_ready()
    return safe_response({
        "session": {
            "active": False,
            "ready": ready,
            "livekit_configured": _livekit_ready(),
            "gemini_realtime_configured": _gemini_ready(),
            "state": "session_ready" if ready else "not_configured",
            "room": None,
            "identity": None,
            "token_issued": False,
        },
        "message": "Sessao pronta para iniciar. Clique em Iniciar Sessao." if ready else "Sessao nao configurada. Configure LiveKit e Gemini Realtime.",
        "next_step": "Clique em Iniciar Sessao no Voice Control Center." if ready else "Configure .env com LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET e GEMINI_API_KEY.",
        "token_exposed": False,
    })


class SessionCreateRequest(BaseModel):
    room_name: Optional[str] = None
    identity: str = "tokyo-user"

@app.post("/tokyo/voice/session/create")
async def voice_session_create(req: SessionCreateRequest):
    if not _livekit_ready():
        return safe_response({"success": True, "status": "not_configured",
            "session_token_issued": False, "token_exposed": False,
            "next_step": "Configure LiveKit credentials in .env."})

    from tokyo_voice_agent.dispatch import create_session_with_dispatch as make_session
    result = await make_session(req.identity)
    return safe_response(result)


class SessionStopRequest(BaseModel):
    room: str = ""
    identity: str = ""

@app.post("/tokyo/voice/session/stop")
async def voice_session_stop(req: SessionStopRequest):
    return safe_response({
        "success": True,
        "status": "session_stopped_local",
        "room": req.room,
        "message": "Sessao encerrada localmente. Recursos de microfone e audio liberados no navegador.",
        "warning": "O processo backend da TokyoOS (agent.py/LiveKit worker) NAO foi interrompido. Apenas a sessao do navegador foi encerrada.",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/speech/status")
async def voice_speech_status_v2():
    lk = _livekit_ready()
    gm = _gemini_ready()
    ready = lk and gm
    state = "session_ready" if ready else ("not_configured" if not lk else "configured_but_not_triggered")
    return safe_response({
        "speech": {
            "enabled": ready,
            "state": state,
            "provider": "LiveKit + Gemini Realtime",
            "voice_name": "Charon",
            "livekit_configured": lk,
            "gemini_realtime_configured": gm,
            "session_token_available": lk,
            "last_voice_error": None,
        },
        "browser": {
            "requires_user_gesture": True,
            "autoplay_policy": "user_activation_required",
            "recommendation": "Clique em 'Iniciar Sessao' para ativar o audio no navegador.",
        },
        "next_step": "Clique em Iniciar Sessao para comecar." if ready else "Configure LiveKit e Gemini Realtime no .env.",
        "token_exposed": False,
    })


class SpeechTestV2Request(BaseModel):
    text: str = "Tokyo online. Sistema de voz pronto."

@app.post("/tokyo/voice/speech/test")
async def voice_speech_test_v2(req: SpeechTestV2Request):
    ready = _livekit_ready() and _gemini_ready()
    return safe_response({
        "requested_text": req.text,
        "status": "preview_only" if not ready else "configured_but_needs_session",
        "speech_ready": ready,
        "message": "Para fala real: inicie uma sessao LiveKit. O TTS Gemini Realtime processa dentro da sessao." if ready else "TTS nao configurado. Configure LiveKit e Gemini Realtime.",
        "next_step": "Inicie sessao no Voice Control Center para testar fala real." if ready else "Configure .env.",
        "action": "preview_only",
        "executed": False,
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 4C: VOICE AGENT ENDPOINTS
# ═══════════════════════════════════════════════════════════

from tokyo_voice_agent.config import is_configured as agent_configured, check_config, AGENT_MODE, AGENT_VOICE, AGENT_LANGUAGE
from tokyo_voice_agent.status import get as agent_state_get, log_event as agent_log_event


@app.get("/tokyo/voice/agent/status")
async def voice_agent_status():
    st = agent_state_get()
    return safe_response({
        "agent": {
            "enabled": agent_configured(),
            "configured": agent_configured(),
            "mode": AGENT_MODE,
            "safe_mode": AGENT_MODE == "safe",
            "voice": AGENT_VOICE,
            "language": AGENT_LANGUAGE,
            "worker_running": st.get("worker_running", False),
            "room_joined": st.get("room_joined", False),
            "room_name": st.get("room_name"),
            "last_event": st.get("last_event"),
            "external_tools_enabled": False,
            "destructive_actions_enabled": False,
            "errors": st.get("errors", []),
        },
        "message": "Agent pronto para iniciar." if agent_configured() else "Agent nao configurado.",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/agent/readiness")
async def voice_agent_readiness():
    return safe_response({
        "ready": agent_configured(),
        "livekit_configured": _livekit_ready(),
        "gemini_realtime_configured": _gemini_ready(),
        "worker_startable": agent_configured(),
        "safe_mode_active": AGENT_MODE == "safe",
        "next_step": "Execute python scripts/run_tokyo_voice_agent.py --room ROOM_NAME" if agent_configured() else "Configure LiveKit e Gemini Realtime no .env.",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/agent/config-check")
async def voice_agent_config_check():
    cfg = check_config()
    return safe_response({
        "config": {
            "livekit_url_configured": cfg["livekit_url"],
            "livekit_api_key_configured": cfg["livekit_api_key"],
            "livekit_api_secret_configured": cfg["livekit_api_secret"],
            "gemini_api_key_configured": cfg["gemini_api_key"],
            "gemini_model": cfg["gemini_model"],
            "all_configured": cfg["configured"],
            "mode": cfg["mode"],
            "voice": cfg["voice"],
        },
        "token_exposed": False,
        "_note": "Nenhum secret exposto. Apenas booleanos.",
    })


@app.get("/tokyo/voice/agent/rooms")
async def voice_agent_rooms():
    st = agent_state_get()
    return safe_response({
        "rooms": [{"room": st.get("room_name"), "joined": st.get("room_joined")}] if st.get("room_name") else [],
        "active_room": st.get("room_name") if st.get("room_joined") else None,
        "token_exposed": False,
    })


@app.post("/tokyo/voice/agent/start-preview")
async def voice_agent_start_preview():
    return safe_response({
        "started": False,
        "status": "manual_required",
        "reason": "Agente Tokyo deve ser iniciado manualmente. Execute: python scripts/run_tokyo_voice_agent.py --room ROOM_NAME",
        "safe_mode": True,
        "token_exposed": False,
    })


@app.post("/tokyo/voice/agent/stop-preview")
async def voice_agent_stop_preview():
    return safe_response({
        "stopped": False,
        "status": "manual_required",
        "reason": "Pare o agente com Ctrl+C no terminal onde o worker estiver rodando.",
        "safe_mode": True,
        "token_exposed": False,
    })


@app.get("/tokyo/voice/bidirectional/status")
async def voice_bidirectional_status():
    st = agent_state_get()
    return safe_response({
        "bidirectional": {
            "browser_client_ready": True,
            "livekit_session_ready": _livekit_ready(),
            "agent_worker_ready": agent_configured(),
            "agent_joined_room": st.get("room_joined", False),
            "agent_room": st.get("room_name"),
            "microphone_published": None,
            "remote_audio_received": None,
            "gemini_realtime_ready": _gemini_ready(),
            "tokyo_can_speak": agent_configured() and st.get("room_joined", False),
        },
        "next_step": "Inicie o agente com scripts/run_tokyo_voice_agent.py --room ROOM" if agent_configured() and not st.get("room_joined") else "",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 4D: SAFE AGENT RUNTIME ENDPOINTS
# ═══════════════════════════════════════════════════════════

from tokyo_voice_agent.runtime_manager import (
    start_agent, stop_agent, get_runtime_status, cleanup_finished, validate_room_name
)

CONFIRM_START = "START_TOKYO_AGENT"
CONFIRM_STOP = "STOP_TOKYO_AGENT"

class AgentStartRequest(BaseModel):
    room: str
    confirm: Optional[str] = None

class AgentStopRequest(BaseModel):
    room: str
    confirm: Optional[str] = None

class ClientEventRequest(BaseModel):
    event: str
    room: str


@app.post("/tokyo/voice/agent/start")
async def voice_agent_start(req: AgentStartRequest):
    if req.confirm != CONFIRM_START:
        return safe_response({
            "started": False,
            "status": "requires_confirmation",
            "message": f"Envie 'confirm': '{CONFIRM_START}' para iniciar o agente.",
            "next_step": "Reenvie o POST com confirm = 'START_TOKYO_AGENT'.",
            "token_exposed": False,
        })
    result = start_agent(req.room)
    return safe_response(result)


@app.post("/tokyo/voice/agent/stop")
async def voice_agent_stop(req: AgentStopRequest):
    if req.confirm != CONFIRM_STOP:
        return safe_response({
            "stopped": False,
            "status": "requires_confirmation",
            "message": f"Envie 'confirm': '{CONFIRM_STOP}' para parar o agente.",
            "next_step": "Reenvie o POST com confirm = 'STOP_TOKYO_AGENT'.",
            "token_exposed": False,
        })
    result = stop_agent(req.room)
    return safe_response(result)


@app.get("/tokyo/voice/agent/runtime")
async def voice_agent_runtime():
    cleanup_finished()
    status = get_runtime_status()
    return safe_response(status)


@app.get("/tokyo/voice/agent/workers")
async def voice_agent_workers():
    return voice_agent_runtime()


@app.post("/tokyo/voice/bidirectional/mark-client-event")
async def voice_bidirectional_mark_event(req: ClientEventRequest):
    from tokyo_voice_agent.status import update, log_event
    if req.event in ("remote_audio_received", "mic_published", "agent_audio_playing"):
        update(last_event=req.event)
        log_event(req.event, {"room": req.room})
    return safe_response({
        "recorded": True,
        "event": req.event,
        "room": req.room,
        "note": "Evento registrado. Audio nunca salvo ou enviado por este endpoint.",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 4E: E2E VOICE TEST MODE + AUTO TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════

_e2e_state = {"active": False, "room": None, "steps": {}}

CRITERIA = [
    "session_created",
    "browser_connected",
    "mic_permission_granted",
    "mic_published",
    "agent_start_requested",
    "agent_worker_running",
    "agent_joined_room",
    "user_audio_detected",
    "gemini_realtime_connected",
    "gemini_response_started",
    "tokyo_audio_published",
    "remote_audio_received",
    "audio_playback_started",
    "tokyo_spoke_successfully",
]


class E2EMarkRequest(BaseModel):
    room: str
    event: str
    metadata: Optional[dict] = None


@app.get("/tokyo/voice/e2e/status")
async def voice_e2e_status():
    completed = sum(1 for s in CRITERIA if _e2e_state["steps"].get(s))
    return safe_response({
        "e2e": {
            "active": _e2e_state["active"],
            "room": _e2e_state["room"],
            "criteria": CRITERIA,
            "completed": completed,
            "total": len(CRITERIA),
            "steps": {s: _e2e_state["steps"].get(s, False) for s in CRITERIA},
            "ready": completed == len(CRITERIA),
            "status": "success" if completed == len(CRITERIA) else ("partial" if completed > 3 else "not_started"),
        },
        "token_exposed": False,
    })


@app.post("/tokyo/voice/e2e/start-test")
async def voice_e2e_start():
    _e2e_state["active"] = True
    _e2e_state["steps"] = {}
    from tokyo_voice_agent.status import log_event
    log_event("e2e_test_started", {})
    return safe_response({
        "started": True,
        "message": "E2E test started. Use /tokyo/voice/e2e/mark-event to record steps, or they will be detected automatically.",
        "token_exposed": False,
    })


@app.post("/tokyo/voice/e2e/stop-test")
async def voice_e2e_stop():
    _e2e_state["active"] = False
    from tokyo_voice_agent.status import log_event
    log_event("e2e_test_stopped", {"completed": sum(1 for s in CRITERIA if _e2e_state["steps"].get(s))})
    return safe_response({"stopped": True, "token_exposed": False})


@app.post("/tokyo/voice/e2e/mark-event")
async def voice_e2e_mark_event(req: E2EMarkRequest):
    if req.event not in CRITERIA:
        return safe_response({"recorded": False, "error": f"Unknown event: {req.event}", "valid_events": CRITERIA})
    if req.metadata:
        safe_meta = {}
        for k, v in req.metadata.items():
            if any(s in str(k).lower() for s in ("token", "secret", "key", "password", "audio", "base64", "blob")):
                safe_meta[k] = "***FILTERED***"
            else:
                safe_meta[k] = v
        req.metadata = safe_meta
    _e2e_state["steps"][req.event] = True
    from tokyo_voice_agent.status import log_event
    log_event(f"e2e_{req.event}", {"room": req.room})
    return safe_response({"recorded": True, "event": req.event, "token_exposed": False})


@app.get("/tokyo/voice/e2e/report")
async def voice_e2e_report():
    return await voice_e2e_status()


@app.get("/tokyo/voice/e2e/troubleshoot")
async def voice_e2e_troubleshoot():
    lk = _livekit_ready()
    gm = _gemini_ready()
    st = agent_state_get()
    agent_ok = agent_configured()
    worker_running = st.get("worker_running", False)

    failures = []
    layer = None

    # Browser checks
    if not lk:
        failures.append("browser: LiveKit not configured, frontend cannot connect")
        layer = layer or "livekit"

    # LiveKit checks
    if not env_present("LIVEKIT_URL"):
        failures.append("livekit: LIVEKIT_URL missing")
        layer = layer or "livekit"
    if not env_present("LIVEKIT_API_KEY"):
        failures.append("livekit: LIVEKIT_API_KEY missing")
        layer = layer or "livekit"
    if not env_present("LIVEKIT_API_SECRET"):
        failures.append("livekit: LIVEKIT_API_SECRET missing")
        layer = layer or "livekit"

    # Agent checks
    if not agent_ok:
        failures.append("agent: Agent not configured (check LiveKit + Gemini)")
        layer = layer or "agent"
    elif not worker_running:
        failures.append("agent: Worker not running. Start via UI or manually.")
        layer = layer or "agent"

    # Gemini checks
    if not gm:
        failures.append("gemini: GEMINI_API_KEY missing")
        layer = layer or "gemini"

    # Security checks
    btn = "START_TOKYO_AGENT" in (BASE_DIR / "interface" / "index.html").read_text() if (BASE_DIR / "interface" / "index.html").exists() else False

    if not failures:
        overall = "ready"
        cause = "All systems configured. Start session and agent to test."
        fix = "1. Open /ui → Voz. 2. Iniciar Sessao. 3. Ligar Mic. 4. Iniciar Agente. 5. Speak."
    elif len(failures) <= 2:
        overall = "partial"
        cause = failures[0]
        fix = "Fix the reported issue(s) and retry."
    else:
        overall = "blocked"
        cause = failures[0]
        fix = "Multiple issues. Check .env configuration first."

    return safe_response({
        "overall_status": overall,
        "failed_layer": layer,
        "failures": failures,
        "probable_cause": cause,
        "recommended_fix": fix,
        "safe_to_continue": True,
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 4G: WORKER DISPATCH ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/voice/worker/status")
async def voice_worker_status():
    st = agent_state_get()
    rt = get_runtime_status()
    return safe_response({
        "worker": {
            "process_running": any(w["running"] for w in rt.get("workers", [])),
            "registered": st.get("worker_running", False),
            "waiting_for_dispatch": st.get("worker_running", False) and not st.get("room_joined", False),
            "room_joined": st.get("room_joined", False),
            "last_room": st.get("room_name"),
            "last_event": st.get("last_event"),
            "errors": st.get("errors", []),
            "safe_mode": True,
        },
        "workers_managed": rt.get("workers", []),
        "next_step": "Worker nao esta rodando. Execute: python scripts/run_tokyo_voice_agent.py" if not st.get("worker_running") else "Worker rodando. Crie uma sessao no navegador.",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/worker/dispatch-status")
async def voice_worker_dispatch_status():
    st = agent_state_get()
    return safe_response({
        "dispatch": {
            "worker_registered": st.get("worker_running", False),
            "waiting_for_job": st.get("worker_running", False) and not st.get("room_joined", False),
            "job_received": st.get("room_joined", False),
            "agent_joined_room": st.get("room_joined", False),
            "last_room": st.get("room_name"),
        },
        "message": "Worker registrado aguardando dispatch do LiveKit." if st.get("worker_running") and not st.get("room_joined") else ("Agent joined room: " + str(st.get("room_joined"))),
        "token_exposed": False,
    })


@app.get("/tokyo/voice/dispatch/readiness")
async def voice_dispatch_readiness():
    lk = _livekit_ready()
    gm = _gemini_ready()
    st = agent_state_get()
    return safe_response({
        "readiness": {
            "livekit_configured": lk,
            "gemini_configured": gm,
            "agent_configured": agent_configured(),
            "worker_script_exists": (BASE_DIR / "scripts" / "run_tokyo_voice_agent.py").exists(),
            "worker_running": st.get("worker_running", False),
            "dispatch_supported": True,
            "auto_dispatch_expected": True,
        },
        "ready": lk and gm and agent_configured() and st.get("worker_running", False),
        "next_step": "Execute python scripts/run_tokyo_voice_agent.py para registrar o worker." if not st.get("worker_running") else "Crie uma sessao no navegador para o LiveKit despachar o agente.",
        "token_exposed": False,
    })


@app.get("/tokyo/voice/dispatch/status")
async def voice_dispatch_status():
    return await voice_worker_dispatch_status()


class DispatchCreateRequest(BaseModel):
    room: str
    confirm: Optional[str] = None

@app.post("/tokyo/voice/dispatch/create")
async def voice_dispatch_create(req: DispatchCreateRequest):
    if req.confirm != "DISPATCH_TOKYO_AGENT":
        return safe_response({
            "dispatch_requested": False,
            "status": "requires_confirmation",
            "message": "Envie 'confirm': 'DISPATCH_TOKYO_AGENT'.",
            "token_exposed": False,
        })
    # LiveKit Agents SDK auto-dispatches via JobContext; no manual dispatch in SDK
    return safe_response({
        "dispatch_requested": True,
        "status": "auto_dispatch_active",
        "message": "O LiveKit Agents SDK despacha jobs automaticamente quando o worker esta registrado e o usuario conecta na sala. Nao ha API manual no SDK. Basta: 1) rodar worker, 2) criar sessao no navegador.",
        "next_step": "1. python scripts/run_tokyo_voice_agent.py  2. Abra /ui > Voice > Iniciar Sessao",
        "token_exposed": False,
    })


# ═══════════════════════════════════════════════════════════
# PHASE 4I: EXPLICIT AGENT DISPATCH
# ═══════════════════════════════════════════════════════════

from tokyo_voice_agent.dispatch import (
    check_capability, create_dispatch, get_last_dispatch, create_session_with_dispatch,
)

@app.get("/tokyo/voice/dispatch/capability")
async def voice_dispatch_capability():
    return safe_response(check_capability())


@app.post("/tokyo/voice/dispatch/create")
async def voice_dispatch_create_v2(req: DispatchCreateRequest):
    if req.confirm != "DISPATCH_TOKYO_AGENT":
        return safe_response({"dispatch_requested": False, "status": "requires_confirmation",
                              "message": "Envie 'confirm': 'DISPATCH_TOKYO_AGENT'.", "token_exposed": False})
    if req.room:
        result = create_dispatch(req.room)
        return safe_response(result)
    return safe_response({"dispatch_requested": False, "error": "room required", "token_exposed": False})


@app.get("/tokyo/voice/dispatch/latest")
async def voice_dispatch_latest():
    return safe_response(get_last_dispatch())


# ═══════════════════════════════════════════════════════════
# PHASE 4I: TOKYO INTERNAL API KEY CENTER
# ═══════════════════════════════════════════════════════════

from tokyo_security.api_keys import (
    generate_api_key, verify_api_key, list_api_keys, revoke_api_key, rotate_api_key,
)

class APIKeyCreateRequest(BaseModel):
    name: str
    scopes: Optional[list] = None
    confirm: Optional[str] = None

class APIKeyRevokeRequest(BaseModel):
    key_id: str
    confirm: Optional[str] = None

class APIKeyVerifyRequest(BaseModel):
    key: str


@app.get("/tokyo/security/api-keys/status")
async def api_keys_status():
    keys = list_api_keys()
    return safe_response({"api_keys_count": len(keys), "active": sum(1 for k in keys if not k.get("revoked")),
                          "token_exposed": False})


@app.get("/tokyo/security/api-keys")
async def api_keys_list():
    return safe_response({"api_keys": list_api_keys(), "token_exposed": False})


@app.post("/tokyo/security/api-keys/create")
async def api_keys_create(req: APIKeyCreateRequest):
    if req.confirm != "CREATE_TOKYO_API_KEY":
        return safe_response({"created": False, "status": "requires_confirmation",
                              "message": "Envie 'confirm': 'CREATE_TOKYO_API_KEY'.", "token_exposed": False})
    result = generate_api_key(req.name, req.scopes)
    return safe_response(result)


@app.post("/tokyo/security/api-keys/revoke")
async def api_keys_revoke(req: APIKeyRevokeRequest):
    if req.confirm != "REVOKE_TOKYO_API_KEY":
        return safe_response({"revoked": False, "status": "requires_confirmation",
                              "message": "Envie 'confirm': 'REVOKE_TOKYO_API_KEY'.", "token_exposed": False})
    return safe_response(revoke_api_key(req.key_id))


@app.post("/tokyo/security/api-keys/rotate")
async def api_keys_rotate(req: APIKeyRevokeRequest):
    if req.confirm != "ROTATE_TOKYO_API_KEY":
        return safe_response({"rotated": False, "status": "requires_confirmation",
                              "message": "Envie 'confirm': 'ROTATE_TOKYO_API_KEY'.", "token_exposed": False})
    return safe_response(rotate_api_key(req.key_id))


@app.post("/tokyo/security/api-keys/verify")
async def api_keys_verify(req: APIKeyVerifyRequest):
    result = verify_api_key(req.key)
    return safe_response({"verification": result, "note": "Key never stored or logged.", "token_exposed": False})


# ═══════════════════════════════════════════════════════════
# HOTFIX 4I.1: UI STATUS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/tokyo/ui/status")
async def ui_status():
    html_path = INTERFACE_DIR / "index.html"
    html_ok = html_path.exists() and html_path.stat().st_size > 1000
    return safe_response({
        "ui": {
            "html_ok": html_ok,
            "html_size_bytes": html_path.stat().st_size if html_path.exists() else 0,
            "routes_count": 60,
            "default_page": "page-home",
            "last_error": None,
        },
        "token_exposed": False,
    })


@app.get("/tokyo/ui/routes")
async def ui_routes():
    return safe_response({
        "routes": [
            {"path": "/ui", "page": "page-home", "title": "Home"},
            {"path": "/ui#page-voice", "page": "page-voice", "title": "Voice Center"},
            {"path": "/ui#page-grupsbunny", "page": "page-grupsbunny", "title": "GrupsBunny"},
            {"path": "/ui#page-finance", "page": "page-finance", "title": "Financeiro"},
            {"path": "/ui#page-apihub", "page": "page-apihub", "title": "API Hub"},
            {"path": "/ui#page-mcp", "page": "page-mcp", "title": "MCP Panel"},
            {"path": "/ui#page-tools", "page": "page-tools", "title": "Tools"},
            {"path": "/ui#page-tools-store", "page": "page-tools-store", "title": "Tools Store"},
            {"path": "/ui#page-deploy", "page": "page-deploy", "title": "Deploy"},
            {"path": "/ui#page-zimaos", "page": "page-zimaos", "title": "ZimaOS"},
            {"path": "/ui#page-system", "page": "page-system", "title": "Sistema"},
            {"path": "/ui#page-comms", "page": "page-comms", "title": "Comunicacao"},
            {"path": "/ui#page-intel", "page": "page-intel", "title": "Inteligencia"},
            {"path": "/ui#page-api-keys", "page": "page-api-keys", "title": "API Keys"},
            {"path": "/setup", "page": "setup-page", "title": "Setup Wizard"},
        ],
        "token_exposed": False,
    })


@app.get("/tokyo/ui/assets-status")
async def ui_assets_status():
    html_path = INTERFACE_DIR / "index.html"
    html_ok = html_path.exists()
    html_size = html_path.stat().st_size if html_ok else 0
    return safe_response({
        "html_ok": html_ok,
        "html_size": html_size,
        "includes_sidebar": "sidebar" in (html_path.read_text() if html_ok else ""),
        "includes_topbar": "topbar" in (html_path.read_text() if html_ok else ""),
        "page_count": (html_path.read_text().count('class="page"') if html_ok else 0),
        "has_livekit_sdk": "livekit-client" in (html_path.read_text() if html_ok else ""),
        "token_exposed": False,
    })

# ═══════════════════════════════════════════════════════════
# HOTFIX 5G.1: OPERATOR ENDPOINTS
# ═══════════════════════════════════════════════════════════

class OperatorExecuteRequest(BaseModel):
    command: str
    mode: str = "company_operator"

@app.get("/tokyo/operator/status")
async def operator_status():
    return safe_response({
        "status": "active",
        "mode": "company_operator",
        "automation_enabled": True,
        "browser_automation_enabled": True,
        "demo_only": False,
        "dry_run_only": False,
        "workspace_available": True,
        "llm_provider": "ollama",
        "llm_model": "qwen2.5:32b-instruct"
    })

@app.post("/tokyo/operator/execute")
async def operator_execute(req: OperatorExecuteRequest):
    from tokyo_plugins.hermes_bridge.service import HermesService
    from tokyo_plugins.hermes_bridge.schemas import HermesExecuteRequest
    svc = HermesService()
    
    # Check for RM -RF blocked
    if "rm -rf" in req.command.lower() and "tokyoos_src" in req.command.lower():
        return safe_response({
            "ok": False,
            "status": "failed",
            "reason": "blocked_project_protection",
            "not_allowed_reason": "blocked_by_safety_gate"
        })

    # Execute
    res = svc.execute_command(HermesExecuteRequest(command=req.command, mode=req.mode))
    
    return safe_response({
        "ok": res.ok,
        "status": res.status,
        "job_id": res.job_id or "local_job",
        "provider_used": "shim/playwright/ollama",
        "action_executed": True,
        "demo_only": False,
        "dry_run": False,
        "summary": res.summary,
        "evidence": {"actions": res.actions_executed},
        "token_exposed": False,
        "reason": res.error
    })

@app.get("/tokyo/operator/jobs")
async def operator_jobs():
    from tokyo_plugins.hermes_bridge.hermes_shim import shim_get_all_jobs
    return safe_response({
        "jobs": shim_get_all_jobs(),
        "token_exposed": False
    })

@app.get("/tokyo/operator/workspace")
async def operator_workspace():
    import os
    workspace_dir = os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace"
    files = []
    if os.path.exists(workspace_dir):
        files = [{"name": f, "path": os.path.join(workspace_dir, f), "size_bytes": os.path.getsize(os.path.join(workspace_dir, f))} for f in os.listdir(workspace_dir)]
    return safe_response({
        "workspace": workspace_dir,
        "files": files,
        "token_exposed": False
    })

@app.get("/tokyo/operator/workspace/read")
async def operator_workspace_read(filename: str):
    import os
    from pathlib import Path
    
    # Security: Ensure filename is just a basename (no path traversal)
    clean_filename = Path(filename).name
    if not clean_filename or clean_filename != filename:
        return safe_response({"ok": False, "error": "Invalid filename", "token_exposed": False})
        
    # Security: Do not allow reading .env files
    if clean_filename == ".env" or clean_filename.endswith(".env"):
        return safe_response({"ok": False, "error": "Cannot read environment files", "token_exposed": False})
        
    workspace_dir = os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace"
    file_path = os.path.join(workspace_dir, clean_filename)
    
    if not os.path.exists(file_path):
        return safe_response({"ok": False, "error": "File not found", "token_exposed": False})
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return safe_response({
            "ok": True,
            "filename": clean_filename,
            "content": content,
            "token_exposed": False
        })
    except Exception as e:
        return safe_response({"ok": False, "error": str(e), "token_exposed": False})

class ActionExecuteRequest(BaseModel):
    command: str
    source: str = "ui_chat"
    mode: str = "company_operator"

@app.post("/tokyo/action/execute")
async def action_gateway_execute(req: ActionExecuteRequest):
    """
    Novo Action Gateway (Phase 6B) usando Tokyo Orchestrator LLM.
    """
    try:
        command = req.command
        
        # Security: Do not allow raw script injections directly from UI input
        if "rm -rf" in command or "sudo" in command:
            return safe_response({"ok": False, "status": "blocked", "error": "Comando destrutivo detectado e bloqueado pela Safety Gate.", "token_exposed": False})
        
        # Usa o Orchestrator (Ollama) para interpretar a intenção
        from tokyo_orchestrator import route_command
        res = route_command(command)
        
        return safe_response(res)

    except Exception as e:
        logger.error(f"Gateway execution error: {str(e)}")
        return safe_response({"ok": False, "status": "failed", "error": str(e), "token_exposed": False})

try:
    from tokyo_mac_bridge.routes import router as mac_bridge_router
    app.include_router(mac_bridge_router)
    logger.info("Mac Mini Bridge router loaded")
except ImportError as e:
    logger.warning(f"Could not load Mac Bridge router: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"TokyoOS starting on {TOKYO_HOST}:{TOKYO_HTTP_PORT}")
    uvicorn.run(app, host=TOKYO_HOST, port=TOKYO_HTTP_PORT, log_level="info")
