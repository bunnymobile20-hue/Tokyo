#!/usr/bin/env python3
"""TokyoOS Phase 3A.1 — UI + Gate Static Test"""
import os, json, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SIB_DIR = BASE_DIR / "siberian_connector"
PASS, FAIL = 0, 0

def ok(n, c, d=""):
    global PASS, FAIL
    (PASS := PASS + 1) if c else (FAIL := FAIL + 1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nTokyoOS Phase 3A.1 — UI + Gate Test\n"+"="*60+"\n")

print("1. UI SISTEMA SIBERIAN")
ui = (BASE_DIR / "interface" / "index.html").read_text() if (BASE_DIR / "interface" / "index.html").exists() else ""
ok("UI has Sistema Siberian section", "Sistema Siberian" in ui)
ok("UI shows read_only mode", "read_only" in ui)
ok("UI shows not_configured status", "not_configured" in ui)
ok("UI shows Safe Mode", "Safe Mode" in ui or "safe_mode" in ui.lower())
ok("UI shows Phase 3A reference", "Phase 3A" in ui or "Connector" in ui)
ok("UI shows config false", "Configurado" in ui and "false" in ui)
ok("UI shows Token Exposed: never", "Token Exposed" in ui or "token_exposed" in ui.lower())
ok("UI has no real URL value", "API_URL" not in ui.upper() or "nao configurada" in ui.lower())
ok("UI has no credential text", "API_KEY" not in ui and "api key" not in ui.lower() and "token=" not in ui.lower())

print("\n2. REAL API READINESS ENDPOINT")
routes = (SIB_DIR / "routes.py").read_text() if (SIB_DIR / "routes.py").exists() else ""
svc = (SIB_DIR / "service.py").read_text() if (SIB_DIR / "service.py").exists() else ""
ok("Route registered", "/real-api-readiness" in routes)
ok("Service function exists", "def get_real_api_readiness" in svc)
ok("Returns ready_for_real_api", "ready_for_real_api" in svc)
ok("Returns allowed_methods", "allowed_methods" in svc)
ok("Returns blocked_methods", "blocked_methods" in svc)
ok("Returns next_step", "next_step" in svc)
ok("Blocks POST/PUT/PATCH/DELETE", all(m in str(svc) for m in ["POST", "PUT", "PATCH", "DELETE"]))
ok("allowed_methods is GET only", '"GET"' in svc or "'GET'" in svc)
ok("token_exposed=False", "token_exposed" in svc.lower() and "false" in (svc.lower()))

print("\n3. SIBERIAN STILL READ-ONLY")
client = (SIB_DIR / "client.py").read_text() if (SIB_DIR / "client.py").exists() else ""
ok("Siberian mode read_only", "read_only" in svc.lower() or "read_only" in client.lower())
ok("No HTTP POST method in client", 'method="POST"' not in client)
ok("No HTTP PUT method in client", 'method="PUT"' not in client)
ok("Upload still disabled", "upload_enabled" in (BASE_DIR / "app.py").read_text())

print("\n4. FINANCE ENGINE PRESERVED")
eng = (BASE_DIR / "finance_engine" / "__init__.py").read_text() if (BASE_DIR / "finance_engine" / "__init__.py").exists() else ""
for fn in ["calculate_dre", "calculate_cash_flow", "calculate_break_even", "calculate_minimum_cash"]:
    ok(f"{fn} preserved", f"def {fn}" in eng)

print("\n5. CODE SAFETY")
for d in ["shell=True", "os.remove", "os.unlink", "shutil.rmtree", "pkill", "killall", "sudo "]:
    for pyf in list(BASE_DIR.glob("*.py")) + list(SIB_DIR.glob("*.py")):
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text(), f"found {d}")

print("\n6. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list(SIB_DIR.glob("*.py")):
    try: py_compile.compile(str(pyf), doraise=True); ok(f"{pyf.name}", True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}", False, str(e))

print(f"\n{'='*60}\nPHASE 3A.1 STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
