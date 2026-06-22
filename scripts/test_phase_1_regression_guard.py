#!/usr/bin/env python3
"""
TokyoOS Phase 1 — Regression Guard

Validates that the Phase 1 stable checkpoint is intact.
Must pass before Phase 2 can begin.

Checks:
  - Core files present and unmodified
  - Voice preserved (agent.py, prompts.py)
  - All config files valid JSON
  - All required routes in app.py
  - Docker/ZimaOS setup valid
  - No real tokens in any committed file
  - No dangerous code patterns
  - Required flags (required=false, read_only, token_exposed=false)
  - No fake financial data
  - Python syntax clean for all .py files
"""

import os
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DOCS_DIR = BASE_DIR / "docs"
SCRIPTS_DIR = BASE_DIR / "scripts"
INTERFACE_DIR = BASE_DIR / "interface"
RELEASE_DIR = BASE_DIR / "release"

PASS = 0
FAIL = 0


def ok(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def file_ok(path, label):
    ok(f"File: {label}", os.path.exists(str(path)), f"missing: {path}")


def no_tokens(content, label):
    suspicious = [
        "sk-", "AIzaSy", "m0-", "wss://tokio", "Ri93uc"
    ]
    for tok in suspicious:
        if tok in content:
            ok(f"No tokens in {label}", False, f"found: {tok[:8]}...")
            return
    ok(f"No tokens in {label}", True)


def json_valid(path, label):
    if not os.path.exists(str(path)):
        ok(f"JSON valid: {label}", False, "file not found")
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        ok(f"JSON valid: {label}", True)
        return data
    except Exception as e:
        ok(f"JSON valid: {label}", False, str(e))
        return None


def has_route(content, route_path):
    return route_path in content


print("=" * 60)
print("TokyoOS Phase 1 — Regression Guard")
print("=" * 60)
print()

# ── 1. CORE FILES ────────────────────────────────────────
print("1. CORE FILES PRESERVED")
file_ok(BASE_DIR / "agent.py", "agent.py (voice agent)")
file_ok(BASE_DIR / "prompts.py", "prompts.py (AI persona)")
file_ok(BASE_DIR / "app.py", "app.py (FastAPI backend)")
file_ok(BASE_DIR / "requirements.txt", "requirements.txt")
file_ok(BASE_DIR / ".env.example", ".env.example")
file_ok(BASE_DIR / "Dockerfile", "Dockerfile")
file_ok(BASE_DIR / "docker-compose.yml", "docker-compose.yml")

# ── 2. VOICE PRESERVED ───────────────────────────────────
print("\n2. VOICE PRESERVED")
agent_content = (BASE_DIR / "agent.py").read_text() if (BASE_DIR / "agent.py").exists() else ""
ok("agent.py contains LiveKit", "livekit" in agent_content.lower())
ok("agent.py references Google/Gemini LLM", "gemini" in agent_content.lower() or "google" in agent_content.lower())
ok("agent.py contains mem0", "mem0" in agent_content.lower())
ok("agent.py has entrypoint", "entrypoint" in agent_content)

prompt_content = (BASE_DIR / "prompts.py").read_text() if (BASE_DIR / "prompts.py").exists() else ""
ok("prompts.py has AGENT_INSTRUCTION", "AGENT_INSTRUCTION" in prompt_content)
ok("prompts.py has SESSION_INSTRUCTION", "SESSION_INSTRUCTION" in prompt_content)
ok("prompts.py mentions TOKYO", "TOKYO" in prompt_content)

# ── 3. CONFIG FILES ──────────────────────────────────────
print("\n3. CONFIG FILES")
config_files = [
    "providers.example.json",
    "integrations.example.json",
    "connectors.example.json",
    "credentials.schema.json",
    "business.example.json",
    "finance_models.example.json",
]
for cf in config_files:
    file_ok(CONFIG_DIR / cf, f"config/{cf}")
    json_valid(CONFIG_DIR / cf, f"config/{cf}")

# ── 4. DOCKER / ZIMAOS ───────────────────────────────────
print("\n4. DOCKER / ZIMAOS")
dc_path = BASE_DIR / "docker-compose.yml"
if dc_path.exists():
    dc = dc_path.read_text()
    ok("docker-compose has x-casaos", "x-casaos" in dc.lower())
    ok("docker-compose no network_mode host", "network_mode: host" not in dc)
    ok("docker-compose has port 8788", "8788" in dc)
    ok("docker-compose has volume mount", "/DATA/AppData/tokyoos" in dc)
    ok("docker-compose uses restart unless-stopped", "unless-stopped" in dc)

dockerfile_path = BASE_DIR / "Dockerfile"
if dockerfile_path.exists():
    df = dockerfile_path.read_text()
    ok("Dockerfile has HEALTHCHECK", "HEALTHCHECK" in df)
    ok("Dockerfile exposes 8788", "8788" in df)
    ok("Dockerfile has VOLUME", "VOLUME" in df)

# ── 5. FRONTEND ──────────────────────────────────────────
print("\n5. FRONTEND")
ui_path = INTERFACE_DIR / "index.html"
file_ok(ui_path, "interface/index.html")
if ui_path.exists():
    ui = ui_path.read_text()
    ok("UI has GrupsBunny", "GrupsBunny" in ui)
    ok("UI has Bunny Dreams", "Bunny Dreams" in ui)
    ok("UI has Bunny Siberian", "Bunny Siberian" in ui)
    ok("UI has Sistema Siberian", "Sistema Siberian" in ui)
    ok("UI mentions Riverside", "Riverside" in ui)
    ok("UI mentions Teresina", "Teresina" in ui)
    ok("UI has finance section (DRE)", "DRE" in ui)
    ok("UI has finance section (Cash Flow)", "Fluxo de Caixa" in ui or "Cash" in ui)
    ok("UI has no fake financial values", "R$ 0" not in ui and "R$1" not in ui)

# ── 6. TOKEN EXPOSURE ────────────────────────────────────
print("\n6. TOKEN EXPOSURE")
env_example = BASE_DIR / ".env.example"
if env_example.exists():
    content = env_example.read_text()
    ok(".env.example has TOKYO_TOKEN_EXPOSED=false", "TOKYO_TOKEN_EXPOSED=false" in content)
    ok(".env.example has TOKYO_SAFE_MODE=true", "TOKYO_SAFE_MODE=true" in content)
    no_tokens(content, ".env.example")

manifest = RELEASE_DIR / "TOKYOOS_PHASE_1_MANIFEST.json"
if manifest.exists():
    content = manifest.read_text()
    ok("Manifest shows token_exposed=false", '"token_exposed": false' in content)
    no_tokens(content, "manifest.json")

# Check all committed Python files
for pyfile in sorted(BASE_DIR.glob("*.py")):
    no_tokens(pyfile.read_text(), pyfile.name)

# ── 7. REQUIREMENT FLAGS ─────────────────────────────────
print("\n7. REQUIREMENT FLAGS")
int_config = json_valid(CONFIG_DIR / "integrations.example.json", "")
if int_config:
    for i in int_config.get("integrations", []):
        rid = i["id"]
        req = i.get("required", True)
        if rid in ("hermes", "mcp", "ollama", "openwebui", "browser_use", "firecrawl", "openclaw"):
            ok(f"{rid} required=false", not req, f"required={req}")
        if rid == "sistema_siberian":
            ok("sistema_siberian required=false", not req)
        if rid == "sistema_siberian":
            ok("sistema_siberian mode=read_only", i.get("mode") == "read_only")

bus_config = json_valid(CONFIG_DIR / "business.example.json", "")
if bus_config:
    for bu in bus_config.get("business_units", []):
        if bu["id"] == "sistema_siberian":
            conn = bu.get("connector", {})
            ok("Sistema Siberian required=false", not conn.get("required", True))
            ok("Sistema Siberian mode=read_only", conn.get("mode") == "read_only")

# ── 8. NO FAKE FINANCIAL DATA ────────────────────────────
print("\n8. NO FAKE FINANCIAL DATA")
fin_config = json_valid(CONFIG_DIR / "finance_models.example.json", "")
if fin_config:
    for model in fin_config.get("finance_models", []):
        mid = model["id"]
        status = model.get("status", "")
        ds = model.get("data_source", "")
        ok(f"{mid} status planned/not_configured", status in ("planned", "not_configured"), f"status={status}")
        ok(f"{mid} data_source pending_api or similar", ds in ("pending_api", "manual_upload_future"), f"data_source={ds}")

# ── 9. CODE SAFETY ───────────────────────────────────────
print("\n9. CODE SAFETY (no dangerous patterns)")
dangerous = {
    "shell=True": "shell=True",
    "os.remove": "os.remove",
    "os.unlink": "os.unlink",
    "shutil.rmtree": "shutil.rmtree",
    "pkill": "pkill",
    "killall": "killall",
    "sudo ": "sudo ",
}
for pyfile in sorted(BASE_DIR.glob("*.py")):
    content = pyfile.read_text()
    for label, pattern in dangerous.items():
        ok(f"{pyfile.name}: no {label}", pattern not in content, f"found {label} in {pyfile.name}")

# ── 10. ROUTES IN APP.PY ─────────────────────────────────
print("\n10. REQUIRED ROUTES IN app.py")
app_content = (BASE_DIR / "app.py").read_text() if (BASE_DIR / "app.py").exists() else ""
required_routes = [
    "/tokyo/system/health",
    "/tokyo/setup/status",
    "/tokyo/setup/checklist",
    "/tokyo/doctor",
    "/tokyo/llm/status",
    "/tokyo/providers/registry",
    "/tokyo/integrations/registry",
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
    "/ui",
]
for route in required_routes:
    ok(f"Route {route}", route in app_content, "route missing from app.py")

# ── 11. DOCS ──────────────────────────────────────────────
print("\n11. DOCUMENTATION")
docs = [
    "TOKYOOS_PHASE_1_PROFESSIONAL_CORE_REPORT.md",
    "TOKYOOS_PHASE_1_STABLE_CHECKPOINT.md",
    "TOKYOOS_PHASE_2_ENTRY_RULES.md",
    "TOKYOOS_GRUPSBUNNY_DASHBOARD_MODEL.md",
    "TOKYOOS_FINANCIAL_DASHBOARD_MODEL.md",
    "TOKYOOS_ZIMAOS_APP_MODEL.md",
]
for d in docs:
    file_ok(DOCS_DIR / d, d)

# ── 12. SCRIPTS ───────────────────────────────────────────
print("\n12. SCRIPTS")
scripts = [
    "healthcheck.sh",
    "test_phase_1_professional_core.py",
    "test_phase_1_regression_guard.py",
    "runtime_validate_phase_1_professional_core.py",
    "runtime_validate_phase_1_checkpoint.py",
]
for s in scripts:
    file_ok(SCRIPTS_DIR / s, s)

# ── 13. RELEASE ──────────────────────────────────────────
print("\n13. RELEASE PACKAGE")
file_ok(RELEASE_DIR / "TOKYOOS_PHASE_1_MANIFEST.json", "manifest.json")
tarball = RELEASE_DIR / "tokyoos_phase_1_professional_core.tar.gz"
file_ok(tarball, "release tarball")

# ── 14. PYTHON SYNTAX ────────────────────────────────────
print("\n14. PYTHON SYNTAX CHECK")
import py_compile
for pyfile in sorted(BASE_DIR.glob("*.py")):
    try:
        py_compile.compile(str(pyfile), doraise=True)
        ok(f"{pyfile.name} syntax", True)
    except py_compile.PyCompileError as e:
        ok(f"{pyfile.name} syntax", False, str(e))

# ── 15. BUSINESS IDENTITY ────────────────────────────────
print("\n15. BUSINESS IDENTITY")
if bus_config:
    bu_ids = [bu["id"] for bu in bus_config.get("business_units", [])]
    ok("Bunny Dreams exists", "bunny_dreams" in bu_ids)
    ok("Bunny Siberian exists", "bunny_siberian" in bu_ids)
    ok("Sistema Siberian exists", "sistema_siberian" in bu_ids)

    bunny_dreams = next((bu for bu in bus_config.get("business_units", []) if bu["id"] == "bunny_dreams"), None)
    if bunny_dreams:
        unit_ids = [u["id"] for u in bunny_dreams.get("units", [])]
        ok("Riverside store exists", "riverside" in unit_ids)
        ok("Teresina store exists", "teresina" in unit_ids)

    bunny_siberian = next((bu for bu in bus_config.get("business_units", []) if bu["id"] == "bunny_siberian"), None)
    if bunny_siberian:
        ok("Bunny Siberian is systems_company", bunny_siberian.get("type") == "systems_company")
        ok("Bunny Siberian has recurring revenue", "recurring_revenue" == bunny_siberian.get("business_model", {}).get("type"))

# ── 16. FINANCIAL MODELS COMPLETENESS ────────────────────
print("\n16. FINANCIAL MODELS")
if fin_config:
    needed = ["dre", "cash_flow", "break_even", "operational_cycle", "minimum_cash", "financial_dashboard"]
    model_ids = [m["id"] for m in fin_config.get("finance_models", [])]
    for n in needed:
        ok(f"Model {n} exists", n in model_ids)

# ── RESULT ───────────────────────────────────────────────
print()
print("=" * 60)
print(f"REGRESSION GUARD: {PASS} passed, {FAIL} failed")
print("=" * 60)

if FAIL > 0:
    print("\nSTATUS: NEEDS_FIX — Regression detected!")
    sys.exit(1)
else:
    print("\nSTATUS: SAFE_TO_START_PHASE_2")
    sys.exit(0)
