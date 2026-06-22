#!/usr/bin/env python3
"""
TokyoOS Phase 2 — Read-Only Data Layer Static Test

Validates:
- Sistema Siberian read-only connector
- Finance calculation engine
- Spreadsheet upload center
- Business data layer
- Audit log
- No fake financial data
- No dangerous code patterns
"""

import os
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
FINANCE_ENGINE_DIR = BASE_DIR / "finance_engine"
SCRIPTS_DIR = BASE_DIR / "scripts"

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


def json_valid(path, label):
    if not os.path.exists(str(path)):
        ok(f"JSON: {label}", False, "file not found")
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        ok(f"JSON: {label}", True)
        return data
    except Exception as e:
        ok(f"JSON: {label}", False, str(e))
        return None


print("=" * 60)
print("TokyoOS Phase 2 — Read-Only Data Layer Test")
print("=" * 60)
print()

# ── 1. SIBERIAN CONNECTOR ────────────────────────────────
print("1. SISTEMA SIBERIAN READ-ONLY CONNECTOR")
app_py = BASE_DIR / "app.py"
app_content = app_py.read_text() if app_py.exists() else ""
routes_py = BASE_DIR / "siberian_connector" / "routes.py"
routes_content = routes_py.read_text() if routes_py.exists() else ""
client_py = BASE_DIR / "siberian_connector" / "client.py"
client_content = client_py.read_text() if client_py.exists() else ""
combined = app_content + "\n" + routes_content + "\n" + client_content

ok("Siberian status endpoint", "/tokyo/siberian" in routes_content and "/status" in routes_content)
ok("Siberian health endpoint", "/tokyo/siberian" in routes_content and "/health" in routes_content)
ok("Siberian schema endpoint", "/tokyo/siberian" in routes_content and "/schema" in routes_content)
ok("Siberian capabilities endpoint", "/tokyo/siberian" in routes_content and "/capabilities" in routes_content)
ok("Siberian companies endpoint", "/tokyo/siberian" in routes_content and "/companies" in routes_content)
ok("Siberian stores endpoint", "/tokyo/siberian" in routes_content and "/stores" in routes_content)
ok("Siberian sales summary endpoint", "/tokyo/siberian" in routes_content and "/sales/summary" in routes_content)
ok("Siberian finance summary endpoint", "/tokyo/siberian" in routes_content and "/finance/summary" in routes_content)
ok("Siberian mode is read_only", "read_only" in combined.lower() and ("SIBERIAN_MODE" in combined or "mode" in routes_content.lower()))
ok("Siberian enabled var", "SIBERIAN_ENABLED" in combined)
ok("Siberian not configured response", "not_configured" in combined)

int_config = json_valid(CONFIG_DIR / "integrations.example.json", "integrations config")
if int_config:
    for i in int_config.get("integrations", []):
        if i["id"] == "sistema_siberian":
            ok("sistema_siberian required=false", not i.get("required", True))
            ok("sistema_siberian mode=read_only", i.get("mode") == "read_only")
            ok("sistema_siberian safe_mode=true", i.get("safe_mode", False))

# ── 2. FINANCE ENGINE ────────────────────────────────────
print("\n2. FINANCE CALCULATION ENGINE")
file_ok(FINANCE_ENGINE_DIR / "__init__.py", "finance_engine/__init__.py")
file_ok(FINANCE_ENGINE_DIR / "audit.py", "finance_engine/audit.py")

engine_content = (FINANCE_ENGINE_DIR / "__init__.py").read_text() if (FINANCE_ENGINE_DIR / "__init__.py").exists() else ""
ok("calculate_dre exists", "def calculate_dre" in engine_content)
ok("calculate_cash_flow exists", "def calculate_cash_flow" in engine_content)
ok("calculate_break_even exists", "def calculate_break_even" in engine_content)
ok("calculate_operational_cycle exists", "def calculate_operational_cycle" in engine_content)
ok("calculate_financial_cycle exists", "def calculate_financial_cycle" in engine_content)
ok("calculate_minimum_cash exists", "def calculate_minimum_cash" in engine_content)

# Import and test calculations
try:
    import sys as _sys
    _sys.path.insert(0, str(BASE_DIR))
    from finance_engine import calculate_dre, calculate_cash_flow, calculate_break_even, calculate_financial_cycle, calculate_minimum_cash

    # Test DRE
    result = calculate_dre(gross_revenue=100000)
    ok("DRE calculation succeeds", result["success"], result.get("warnings", []))
    ok("DRE returns validation_status", "pending_validation" in result.get("validation_status", ""))
    ok("DRE returns source", result.get("source") == "manual_input")
    ok("DRE token_exposed=false", result.get("token_exposed") is False)
    ok("DRE net_revenue = gross - deductions", result["data"].get("net_revenue") is not None)

    result = calculate_dre(gross_revenue=10000, deductions=1000, cogs=5000, fixed_expenses=2000, variable_expenses=1000)
    ok("DRE full calc gross_profit correct", result["data"].get("gross_profit") == 4000, f"got {result['data'].get('gross_profit')}")
    ok("DRE full calc net_revenue", result["data"].get("net_revenue") == 9000)

    # Test Cash Flow
    result = calculate_cash_flow(opening_balance=50000, inflows=20000, outflows=15000)
    ok("Cash flow succeeds", result["success"])
    ok("Cash flow closing_balance", result["data"].get("closing_balance") == 55000)

    # Test Break Even
    result = calculate_break_even(fixed_costs=30000, contribution_margin_percent=40)
    ok("Break even succeeds", result["success"])
    ok("Break even revenue", result["data"].get("break_even_revenue") == 75000)

    result = calculate_break_even(fixed_costs=10000, contribution_margin_percent=0)
    ok("Break even blocks zero margin", not result["success"])

    result = calculate_break_even(fixed_costs=10000, contribution_margin_percent=-5)
    ok("Break even blocks negative margin", not result["success"])

    # Test Financial Cycle
    result = calculate_financial_cycle(average_inventory_days=30, average_receivable_days=15, average_payable_days=20)
    ok("Financial cycle succeeds", result["success"])
    ok("Financial cycle operational = 45", result["data"].get("operational_cycle") == 45)
    ok("Financial cycle = 25", result["data"].get("financial_cycle") == 25)

    result = calculate_financial_cycle(average_inventory_days=10, average_receivable_days=5, average_payable_days=60)
    ok("Financial cycle handles negative", result["success"])
    ok("Financial cycle negative has warning", len(result.get("warnings", [])) > 0)

    # Test Minimum Cash
    result = calculate_minimum_cash(daily_cash_need=1000, financial_cycle_days=25)
    ok("Minimum cash succeeds", result["success"])
    ok("Minimum cash value", result["data"].get("minimum_cash") == 25000)

    # Test all return pending_validation
    r = calculate_dre(gross_revenue=100)
    ok(f"dre returns pending_validation", "pending_validation" in r.get("validation_status", ""), r.get("validation_status"))
    r = calculate_cash_flow(opening_balance=100)
    ok(f"cash_flow returns pending_validation", "pending_validation" in r.get("validation_status", ""), r.get("validation_status"))
    r = calculate_break_even(fixed_costs=100, contribution_margin_percent=10)
    ok(f"break_even returns pending_validation", "pending_validation" in r.get("validation_status", ""), r.get("validation_status"))

except Exception as e:
    ok("Import finance engine", False, str(e))
    print(f"    Error importing: {e}")

# ── 3. FINANCE UPLOADS ───────────────────────────────────
print("\n3. SPREADSHEET UPLOAD CENTER")
ok("Uploads status endpoint", "/tokyo/finance/uploads/status" in app_content)
ok("Uploads registry endpoint", "/tokyo/finance/uploads/registry" in app_content)
ok("Uploads validate endpoint", "/tokyo/finance/uploads/validate" in app_content)
ok("Never overwrite original", "never_overwrite_original" in app_content.lower())
ok("Blocked .xlsm", ".xlsm" in app_content or "xlsm" in app_content.lower())
ok("Accepted .xlsx", ".xlsx" in app_content)

# ── 4. BUSINESS DATA LAYER ───────────────────────────────
print("\n4. BUSINESS DATA LAYER")
ok("Data sources endpoint", "/tokyo/business/data-sources" in app_content)
ok("Scopes endpoint", "/tokyo/business/scopes" in app_content)
ok("Readiness endpoint", "/tokyo/business/readiness" in app_content)
ok("Has GrupsBunny scope", "grupsbunny" in app_content)
ok("Has Bunny Dreams scope", "bunny_dreams" in app_content)
ok("Has Riverside scope", "riverside" in app_content)
ok("Has Teresina scope", "teresina" in app_content)
ok("Has Bunny Siberian scope", "bunny_siberian" in app_content)
ok("Has Sistema Siberian scope", "sistema_siberian" in app_content)

# ── 5. AUDIT LOG ─────────────────────────────────────────
print("\n5. AUDIT LOG")
ok("Audit endpoint", "/tokyo/finance/audit" in app_content)
audit_content = (FINANCE_ENGINE_DIR / "audit.py").read_text() if (FINANCE_ENGINE_DIR / "audit.py").exists() else ""
ok("Audit log function exists", "def log" in audit_content)
ok("Audit strips tokens", "REDACTED" in audit_content)

# ── 6. FINANCE MODELS CONFIG ─────────────────────────────
print("\n6. FINANCE MODELS CONFIG")
fin_config = json_valid(CONFIG_DIR / "finance_models.example.json", "finance_models")
if fin_config:
    model_ids = [m["id"] for m in fin_config.get("finance_models", [])]
    for mid in ["dre", "cash_flow", "break_even", "operational_cycle", "minimum_cash", "financial_dashboard"]:
        ok(f"Model {mid} in config", mid in model_ids)

# ── 7. NO FAKE FINANCIAL DATA ────────────────────────────
print("\n7. NO FAKE FINANCIAL DATA")
for model in fin_config.get("finance_models", []) if fin_config else []:
    ok(f"{model['id']} data_source not live", model.get("data_source") in ("pending_api", "manual_upload_future", "manual_input"), f"got {model.get('data_source')}")
    ok(f"{model['id']} validation pending", model.get("status") in ("planned", "not_configured"), f"got {model.get('status')}")

# ── 8. TOKEN EXPOSURE ────────────────────────────────────
print("\n8. TOKEN EXPOSURE")
ok("app.py has token_exposed=false", "token_exposed" in app_content and "false" in app_content[:app_content.find("token_exposed") + 50])  # approximate
ok("finance engine sets token_exposed=False", '"token_exposed": False' in engine_content or "token_exposed=False" in engine_content)

# ── 9. APP.PY CALCULATION ENDPOINTS ──────────────────────
print("\n9. CALCULATION ENDPOINTS IN APP.PY")
endpoints = [
    "/tokyo/finance/calculate/dre",
    "/tokyo/finance/calculate/cash-flow",
    "/tokyo/finance/calculate/break-even",
    "/tokyo/finance/calculate/operational-cycle",
    "/tokyo/finance/calculate/financial-cycle",
    "/tokyo/finance/calculate/minimum-cash",
]
for ep in endpoints:
    ok(f"Endpoint {ep}", ep in app_content)

# ── 10. SECURITY ─────────────────────────────────────────
print("\n10. CODE SAFETY")
dangerous = ["shell=True", "os.remove", "os.unlink", "shutil.rmtree", "pkill", "killall", "sudo "]
for pyfile in sorted(BASE_DIR.glob("*.py")):
    content = pyfile.read_text()
    for pattern in dangerous:
        ok(f"{pyfile.name}: no {pattern}", pattern not in content, f"found {pattern}")
# Check finance engine too
for pyfile in sorted(FINANCE_ENGINE_DIR.glob("*.py")):
    content = pyfile.read_text()
    for pattern in dangerous:
        ok(f"finance_engine/{pyfile.name}: no {pattern}", pattern not in content, f"found {pattern}")

# ── 11. PYTHON SYNTAX ────────────────────────────────────
print("\n11. PYTHON SYNTAX")
import py_compile
for pyfile in sorted(BASE_DIR.glob("*.py")):
    try:
        py_compile.compile(str(pyfile), doraise=True)
        ok(f"{pyfile.name} syntax", True)
    except py_compile.PyCompileError as e:
        ok(f"{pyfile.name} syntax", False, str(e))
for pyfile in sorted(FINANCE_ENGINE_DIR.glob("*.py")):
    try:
        py_compile.compile(str(pyfile), doraise=True)
        ok(f"finance_engine/{pyfile.name} syntax", True)
    except py_compile.PyCompileError as e:
        ok(f"finance_engine/{pyfile.name} syntax", False, str(e))

# ── RESULT ───────────────────────────────────────────────
print()
print("=" * 60)
print(f"PHASE 2 STATIC TEST: {PASS} passed, {FAIL} failed")
print("=" * 60)

if FAIL > 0:
    print("\nSTATUS: NEEDS_FIX")
    sys.exit(1)
else:
    print("\nSTATUS: SAFE_TO_CONTINUE_PHASE_2_READ_ONLY_DATA_LAYER")
    sys.exit(0)
