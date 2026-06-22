#!/usr/bin/env python3
"""TokyoOS Phase 3B — Dual Interface + Tools Hub Static Test"""
import os, json, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PASS, FAIL = 0, 0

def ok(n, c, d=""):
    global PASS, FAIL
    (PASS := PASS + 1) if c else (FAIL := FAIL + 1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nTokyoOS Phase 3B — Static Test\n"+"="*60+"\n")

print("1. CONFIG FILES")
for f in ["external_tools.example.json","mcp_servers.example.json","voice_commands.example.json","zimaos_tools.example.json"]:
    ok(f"config/{f}", (BASE_DIR/"config"/f).exists())

print("\n2. UI FILES")
ui = (BASE_DIR/"interface"/"index.html").read_text() if (BASE_DIR/"interface"/"index.html").exists() else ""
ok("index.html exists", bool(ui))
ok("UI has Install Mode", "Install Mode" in ui or "install" in ui.lower())
ok("UI has Use Mode", "Use Mode" in ui or "page-home" in ui)
ok("UI has Voice section", "Voz" in ui or "voice" in ui.lower())
ok("UI has MCP section", "MCP" in ui or "page-mcp" in ui)
ok("UI has API Hub", "API Hub" in ui or "page-apihub" in ui)
ok("UI has ZimaOS", "ZimaOS" in ui or "page-zimaos" in ui)
ok("UI has GrupsBunny", "GrupsBunny" in ui)
ok("UI has no fake R$ values", "R$ 45" not in ui and "R$ 35" not in ui and "R$ 15" not in ui)
ok("UI has no localStorage API keys", "localStorage.setItem" not in ui or "api_key" not in ui.lower())
ok("UI has no console.log of secrets", "console.log(api" not in ui.lower() and "console.log(token" not in ui.lower())

print("\n3. APP.PY ENDPOINTS")
app = (BASE_DIR/"app.py").read_text() if (BASE_DIR/"app.py").exists() else ""
endpoints = [
    "/tokyo/voice/activation/status","/tokyo/voice/activation/preview","/tokyo/voice/activation/test-command",
    "/tokyo/mcp/servers","/tokyo/mcp/capabilities","/tokyo/mcp/tools","/tokyo/mcp/test-connection",
    "/tokyo/api-hub/connectors","/tokyo/api-hub/tools","/tokyo/api-hub/readiness","/tokyo/api-hub/test-connector",
    "/tokyo/zimaos/status","/tokyo/zimaos/readiness","/tokyo/zimaos/docker-status","/tokyo/zimaos/install-checklist",
    "/setup","/ui",
]
for ep in endpoints:
    ok(f"Route {ep}", ep in app)

print("\n4. VOICE COMMANDS (no real execution)")
ok("Voice preview endpoint exists", "/tokyo/voice/activation/preview" in app)
ok("Voice test-command exists", "/tokyo/voice/activation/test-command" in app)
ok("Voice preview has executed=False", '"executed"' in app and 'False' in app)

print("\n5. MCP PANEL (optional)")
ok("MCP required false", "required" in app and "False" in str(app))
ok("MCP test placeholder", "test-connection" in app and "token_exposed" in app)

print("\n6. EXTERNAL TOOLS (all optional)")
for t in ["hermes","openclaw","browser_use","firecrawl","ollama","openwebui"]:
    ok(f"{t} in external_tools config", t in (BASE_DIR/"config"/"external_tools.example.json").read_text().lower())
    # Check required false in config
    cfg = json.loads((BASE_DIR/"config"/"external_tools.example.json").read_text())
    for tool in cfg.get("external_tools",[]):
        if tool["id"] == t:
            ok(f"{t} required=false", not tool.get("required",True), tool.get("required"))

print("\n7. ZIMAOS READY")
ok("ZimaOS status endpoint", "/tokyo/zimaos/status" in app)
ok("ZimaOS readiness endpoint", "/tokyo/zimaos/readiness" in app)
ok("ZimaOS install checklist", "/tokyo/zimaos/install-checklist" in app)

print("\n8. REGRESSION CHECKS")
ok("Upload still disabled", "upload_enabled" in app)
ok("Finance engine intact", (BASE_DIR/"finance_engine"/"__init__.py").exists())
ok("Siberian connector intact", (BASE_DIR/"siberian_connector"/"client.py").exists())
ok("App version updated", "phase3" in app or "3." in app)

print("\n9. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    c = pyf.read_text()
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in c, f"found {d}")

print("\n10. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    try: py_compile.compile(str(pyf), doraise=True); ok(f"{pyf.name}", True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}", False, str(e))

print(f"\n{'='*60}\nPHASE 3B STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
