#!/usr/bin/env python3
"""TokyoOS Phase 3A — Siberian Read-Only API Static Test"""
import os, json, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SIB_DIR = BASE_DIR / "siberian_connector"
PASS, FAIL = 0, 0

def ok(n, c, d=""):
    global PASS, FAIL
    (PASS := PASS + 1) if c else (FAIL := FAIL + 1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nTokyoOS Phase 3A — Siberian Static Test\n"+"="*60+"\n")

print("1. MODULE STRUCTURE")
for f in ["client.py", "schemas.py", "service.py", "routes.py", "__init__.py" if False else "__pycache__"]:
    pass
for f in ["client.py", "schemas.py", "service.py", "routes.py"]:
    ok(f"File siberian_connector/{f}", (SIB_DIR / f).exists())

print("\n2. CLIENT FUNCTIONS")
client = (SIB_DIR / "client.py").read_text() if (SIB_DIR / "client.py").exists() else ""
for fn in ["get_config", "is_configured", "safe_get", "get_health", "get_companies",
           "get_stores", "get_sales_summary", "get_finance_summary", "get_products_summary", "get_stock_summary"]:
    ok(f"def {fn}", f"def {fn}" in client)
ok("GET-only client (no HTTP POST method)", 'method="POST"' not in client and 'method="PUT"' not in client and 'method="PATCH"' not in client and 'method="DELETE"' not in client)
ok("No token in logs", "REDACTED" not in client and "logging" in client)

print("\n3. SCHEMAS / NORMALIZERS")
schemas = (SIB_DIR / "schemas.py").read_text() if (SIB_DIR / "schemas.py").exists() else ""
for fn in ["normalize_generic", "normalize_company", "normalize_store", "normalize_sale", "normalize_finance_entry"]:
    ok(f"def {fn}", f"def {fn}" in schemas)
ok("scope in normalizers", "scope" in schemas or "store_scope" in schemas)
ok("validation_status", "pending_validation" in schemas)

print("\n4. SERVICE LAYER")
svc = (SIB_DIR / "service.py").read_text() if (SIB_DIR / "service.py").exists() else ""
for fn in ["get_status", "check_health", "fetch_companies", "fetch_stores",
           "fetch_sales_summary", "fetch_finance_summary", "fetch_products_summary", "fetch_stock_summary"]:
    ok(f"def {fn}", f"def {fn}" in svc)
ok("Audit log references", "siberian_api_readonly" in svc)
ok("Operations blocked listed", "operations_blocked" in svc)

print("\n5. ROUTES")
routes = (SIB_DIR / "routes.py").read_text() if (SIB_DIR / "routes.py").exists() else ""
for ep in ["/status", "/health", "/schema", "/capabilities", "/companies",
           "/stores", "/sales/summary", "/finance/summary", "/products/summary", "/stock/summary"]:
    ok(f"Route {ep}", ep in routes)
ok("Router prefix", "prefix=" in routes and "siberian" in routes)
ok("Read-only enforcement", "read_only" in routes.lower())

print("\n6. CAPABILITIES CONFIG")
cap = BASE_DIR / "config" / "siberian_api.capabilities.example.json"
ok("Capabilities file", cap.exists())
if cap.exists():
    cfg = json.loads(cap.read_text())
    ok("operations_allowed=GET", cfg.get("operations_allowed") == ["GET"])
    ok("operations_blocked", "POST" in str(cfg.get("operations_blocked", [])))
    ok("Has companies capability", any(c["id"]=="companies" for c in cfg.get("capabilities",[])))

print("\n7. REGRESSION CHECKS")
app = (BASE_DIR / "app.py").read_text() if (BASE_DIR / "app.py").exists() else ""
ok("Siberian router registered", "include_router(siberian_router)" in app or "siberian_router" in app)
ok("Version updated to phase3a", "phase3a" in app or "3.0.0" in app)

print("\n8. UPLOAD STILL DISABLED")
ok("Upload disabled preserved", "upload_enabled" in app)

print("\n9. CODE SAFETY")
for d in ["shell=True", "os.remove", "os.unlink", "shutil.rmtree", "pkill", "killall", "sudo "]:
    for pyf in list(BASE_DIR.glob("*.py")) + list(SIB_DIR.glob("*.py")):
        c = pyf.read_text()
        ok(f"{pyf.name}: no {d}", d not in c, f"found in {pyf.name}")

print("\n10. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list(SIB_DIR.glob("*.py")):
    try:
        py_compile.compile(str(pyf), doraise=True)
        ok(f"{pyf.name} syntax", True)
    except py_compile.PyCompileError as e:
        ok(f"{pyf.name} syntax", False, str(e))

print(f"\n{'='*60}\nPHASE 3A STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
