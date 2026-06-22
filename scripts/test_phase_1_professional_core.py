#!/usr/bin/env python3
"""
TokyoOS Phase 1 Professional Core — Static Test Suite

Validates all configuration files, code structure, and business rules
without requiring the app to be running.
"""

import os
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DOCS_DIR = BASE_DIR / "docs"
SCRIPTS_DIR = BASE_DIR / "scripts"

PASS = 0
FAIL = 0
WARN = 0

def test(name, condition, detail=""):
    global PASS, FAIL, WARN
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

def warn(name, condition, detail=""):
    global WARN
    if not condition:
        WARN += 1
        print(f"  [WARN] {name} {detail}")

def file_exists(path, label):
    test(f"File exists: {label}", os.path.exists(path), f"at {path}")

def json_valid(path, label):
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
            test(f"JSON valid: {label}", True)
            return data
        except Exception as e:
            test(f"JSON valid: {label}", False, str(e))
            return None
    else:
        test(f"JSON valid: {label}", False, "file not found")
        return None

def no_real_tokens(filepath):
    if not os.path.exists(filepath):
        return True
    with open(filepath) as f:
        content = f.read()
    suspicious = ["sk-", "AIzaSy", "m0-", "wss://", "Ri93uc"]
    for token in suspicious:
        if token in content:
            return False
    return True


print("=" * 60)
print("TokyoOS Phase 1 — Static Test Suite")
print("=" * 60)
print()

# ── Section 1: Project preserved ──────────────────────────
print("1. PROJECT PRESERVATION")
file_exists(BASE_DIR / "agent.py", "agent.py (voice agent)")
file_exists(BASE_DIR / "prompts.py", "prompts.py (AI prompts)")
file_exists(BASE_DIR / "requirements.txt", "requirements.txt")
test("Voice agent preserved", os.path.exists(BASE_DIR / "agent.py"))

# ── Section 2: Config files ───────────────────────────────
print("\n2. CONFIGURATION FILES")
file_exists(CONFIG_DIR / "providers.example.json", "providers.example.json")
file_exists(CONFIG_DIR / "integrations.example.json", "integrations.example.json")
file_exists(CONFIG_DIR / "connectors.example.json", "connectors.example.json")
file_exists(CONFIG_DIR / "credentials.schema.json", "credentials.schema.json")
file_exists(CONFIG_DIR / "business.example.json", "business.example.json")
file_exists(CONFIG_DIR / "finance_models.example.json", "finance_models.example.json")

# ── Section 3: Env files ──────────────────────────────────
print("\n3. ENVIRONMENT FILES")
file_exists(BASE_DIR / ".env.example", ".env.example")
file_exists(BASE_DIR / ".env", ".env")

# ── Section 4: Backend files ──────────────────────────────
print("\n4. BACKEND")
file_exists(BASE_DIR / "app.py", "app.py (FastAPI)")

# ── Section 5: Frontend ───────────────────────────────────
print("\n5. FRONTEND")
file_exists(BASE_DIR / "interface" / "index.html", "interface/index.html")

# ── Section 6: Docker ─────────────────────────────────────
print("\n6. DOCKER / ZIMAOS")
file_exists(BASE_DIR / "Dockerfile", "Dockerfile")
file_exists(BASE_DIR / "docker-compose.yml", "docker-compose.yml")

# Read docker-compose for validation
dc_path = BASE_DIR / "docker-compose.yml"
if dc_path.exists():
    dc_content = dc_path.read_text()
    test("docker-compose has x-casaos", "x-casaos" in dc_content.lower())
    test("docker-compose does NOT use network_mode host", "network_mode: host" not in dc_content)
    test("docker-compose has volume mount", "/DATA/AppData/tokyoos" in dc_content)
    test("docker-compose has port 8788", "8788" in dc_content)

# ── Section 7: JSON Config validation ─────────────────────
print("\n7. JSON CONFIG VALIDATION")

providers = json_valid(CONFIG_DIR / "providers.example.json", "providers.example.json")
integrations = json_valid(CONFIG_DIR / "integrations.example.json", "integrations.example.json")
connectors = json_valid(CONFIG_DIR / "connectors.example.json", "connectors.example.json")
credentials = json_valid(CONFIG_DIR / "credentials.schema.json", "credentials.schema.json")
business = json_valid(CONFIG_DIR / "business.example.json", "business.example.json")
finance = json_valid(CONFIG_DIR / "finance_models.example.json", "finance_models.example.json")

# ── Section 8: Providers ──────────────────────────────────
print("\n8. LLM PROVIDERS")
if providers:
    prov_ids = [p["id"] for p in providers.get("providers", [])]
    test("Gemini provider exists", "gemini" in prov_ids)
    test("OpenAI provider exists", "openai" in prov_ids)
    test("Ollama provider exists", "ollama" in prov_ids)
    test("OpenWebUI provider exists", "openwebui" in prov_ids)

# ── Section 9: Integration requirements ───────────────────
print("\n9. INTEGRATION REQUIREMENTS (none required)")
if integrations:
    for integration in integrations.get("integrations", []):
        rid = integration["id"]
        req = integration.get("required", False)
        if rid in ("hermes", "mcp", "ollama", "openwebui", "firecrawl", "browser_use", "openclaw"):
            test(f"  {rid} required=false", not req, f"found required={req}")
        if rid == "sistema_siberian":
            test(f"  sistema_siberian required=false", not req)
            test(f"  sistema_siberian mode=read_only", integration.get("mode") == "read_only")

# ── Section 10: Business units ────────────────────────────
print("\n10. BUSINESS UNITS")
if business:
    bu_ids = [bu["id"] for bu in business.get("business_units", [])]
    test("Bunny Dreams exists as business unit", "bunny_dreams" in bu_ids)
    test("Bunny Siberian exists as systems company", "bunny_siberian" in bu_ids)
    test("Sistema Siberian ERP exists as product", "sistema_siberian" in bu_ids)

    # Check Bunny Dreams stores
    bunny_dreams = next((bu for bu in business.get("business_units", []) if bu["id"] == "bunny_dreams"), None)
    if bunny_dreams:
        units = [u["id"] for u in bunny_dreams.get("units", [])]
        test("Riverside store exists", "riverside" in units)
        test("Teresina store exists", "teresina" in units)
        test("Bunny Dreams type is retail", bunny_dreams.get("type") == "retail")

    # Check Bunny Siberian
    bunny_siberian = next((bu for bu in business.get("business_units", []) if bu["id"] == "bunny_siberian"), None)
    if bunny_siberian:
        test("Bunny Siberian type is systems_company", bunny_siberian.get("type") == "systems_company")
        bm = bunny_siberian.get("business_model", {})
        test("Bunny Siberian has recurring_revenue model", bm.get("type") == "recurring_revenue")

    # Check Sistema Siberian
    siberian = next((bu for bu in business.get("business_units", []) if bu["id"] == "sistema_siberian"), None)
    if siberian:
        conn = siberian.get("connector", {})
        test("Sistema Siberian connector required=false", not conn.get("required", True))
        test("Sistema Siberian mode is read_only", conn.get("mode") == "read_only")
        test("Sistema Siberian used internally", "bunny_dreams.riverside" in str(siberian.get("usage", {}).get("internal", [])))

# ── Section 11: Finance models ────────────────────────────
print("\n11. FINANCE MODELS")
if finance:
    model_ids = [m["id"] for m in finance.get("finance_models", [])]
    test("DRE model exists", "dre" in model_ids)
    test("Cash flow model exists", "cash_flow" in model_ids)
    test("Break even model exists", "break_even" in model_ids)
    test("Operational cycle model exists", "operational_cycle" in model_ids)
    test("Minimum cash model exists", "minimum_cash" in model_ids)
    test("Financial dashboard model exists", "financial_dashboard" in model_ids)

    # Verify no fake data
    for model in finance.get("finance_models", []):
        status = model.get("status", "")
        data_source = model.get("data_source", "")
        test(f"  {model['id']} status not active/real", status in ("planned", "not_configured"), f"status={status}")
        warn(f"  {model['id']} data_source not real", data_source not in ("live", "real_api"), f"data_source={data_source}")

# ── Section 12: No dangerous code ─────────────────────────
print("\n12. SECURITY / CODE SAFETY")
for pyfile in BASE_DIR.glob("*.py"):
    content = pyfile.read_text()
    test(f"  {pyfile.name}: no shell=True", "shell=True" not in content)
    test(f"  {pyfile.name}: no os.remove", "os.remove" not in content)
    test(f"  {pyfile.name}: no shutil.rmtree", "shutil.rmtree" not in content)
    test(f"  {pyfile.name}: no pkill", "pkill" not in content)
    test(f"  {pyfile.name}: no killall", "killall" not in content)
    test(f"  {pyfile.name}: no sudo", "sudo" not in content)

# ── Section 13: Token exposure ────────────────────────────
print("\n13. TOKEN EXPOSURE")
env_example = BASE_DIR / ".env.example"
if env_example.exists():
    content = env_example.read_text()
    test("TOKYO_TOKEN_EXPOSED=false in .env.example", "TOKYO_TOKEN_EXPOSED=false" in content)
    test("TOKYO_SAFE_MODE=true in .env.example", "TOKYO_SAFE_MODE=true" in content)

# Verify no real tokens in .env.example
test("No real tokens in .env.example", no_real_tokens(env_example))

# Check app.py for token_exposed references
app_py = BASE_DIR / "app.py"
if app_py.exists():
    content = app_py.read_text()
    token_refs = content.count("token_exposed")
    test(f"app.py references token_exposed ({token_refs} times)", token_refs > 0)

# ── Section 14: Docs ──────────────────────────────────────
print("\n14. DOCUMENTATION")
doc_files = [
    "TOKYOOS_PHASE_1_PROFESSIONAL_CORE_REPORT.md",
    "TOKYOOS_SETUP_MODEL.md",
    "TOKYOOS_API_HUB_MODEL.md",
    "TOKYOOS_PLUGIN_CONNECTOR_MODEL.md",
    "TOKYOOS_MCP_OPTIONAL_MODEL.md",
    "TOKYOOS_PROVIDER_MODEL.md",
    "TOKYOOS_GRUPSBUNNY_DASHBOARD_MODEL.md",
    "TOKYOOS_BUNNY_SIBERIAN_MODEL.md",
    "TOKYOOS_SISTEMA_SIBERIAN_CONNECTOR_MODEL.md",
    "TOKYOOS_FINANCIAL_DASHBOARD_MODEL.md",
    "TOKYOOS_FINANCE_REFERENCE_SPREADSHEETS.md",
    "TOKYOOS_ZIMAOS_APP_MODEL.md",
    "TOKYOOS_UPDATE_MODEL.md",
]
for doc in doc_files:
    file_exists(DOCS_DIR / doc, doc)

# ── Section 15: Scripts ───────────────────────────────────
print("\n15. SCRIPTS")
file_exists(SCRIPTS_DIR / "healthcheck.sh", "healthcheck.sh")
file_exists(SCRIPTS_DIR / "test_phase_1_professional_core.py", "test_phase_1_professional_core.py")
file_exists(SCRIPTS_DIR / "runtime_validate_phase_1_professional_core.py", "runtime_validate_phase_1_professional_core.py")

# ── Section 16: Python syntax check ───────────────────────
print("\n16. PYTHON SYNTAX")
import py_compile
for pyfile in sorted(BASE_DIR.glob("*.py")):
    try:
        py_compile.compile(str(pyfile), doraise=True)
        test(f"  {pyfile.name} syntax OK", True)
    except py_compile.PyCompileError as e:
        test(f"  {pyfile.name} syntax OK", False, str(e))

# ── Result ────────────────────────────────────────────────
print()
print("=" * 60)
print(f"RESULTS: {PASS} passed, {FAIL} failed, {WARN} warnings")
print("=" * 60)

if FAIL > 0:
    print("\nSTATUS: NEEDS_FIX")
    sys.exit(1)
elif WARN > 0:
    print("\nSTATUS: SAFE_TO_CONTINUE_WITH_WARNINGS")
    sys.exit(0)
else:
    print("\nSTATUS: SAFE_TO_CONTINUE_TOKYOOS_PROFESSIONAL_CORE")
    sys.exit(0)
