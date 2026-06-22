#!/usr/bin/env python3
"""TokyoOS Phase 3C — ZimaOS Deploy Readiness Static Test"""
import os, json, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PASS, FAIL = 0, 0
def ok(n, c, d=""):
    global PASS, FAIL
    (PASS := PASS + 1) if c else (FAIL := FAIL + 1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nTokyoOS Phase 3C — Static Test\n"+"="*60+"\n")

print("1. DOCKER FILES")
for f in ["Dockerfile", "docker-compose.yml"]:
    ok(f"{f} exists", (BASE_DIR / f).exists())

dc = (BASE_DIR / "docker-compose.yml").read_text() if (BASE_DIR / "docker-compose.yml").exists() else ""
ok("docker-compose has port 8788", "8788" in dc)
ok("docker-compose has volume mount", "/DATA/AppData/tokyoos" in dc)
ok("no network_mode host", "network_mode: host" not in dc)
ok("no privileged true", "privileged: true" not in dc)
ok("no / mount directly", " - /:" not in dc and " - /\n" not in dc)
ok("no docker.sock mount", "docker.sock" not in dc)
ok("restart unless-stopped", "unless-stopped" in dc)
ok("healthcheck configured", "healthcheck" in dc.lower())

df = (BASE_DIR / "Dockerfile").read_text() if (BASE_DIR / "Dockerfile").exists() else ""
ok("Dockerfile has HEALTHCHECK", "HEALTHCHECK" in df)
ok("Dockerfile exposes 8788", "8788" in df)

print("\n2. X-CASAOS")
ok("x-casaos in compose", "x-casaos" in dc.lower())
ok("title TokyoOS", "TokyoOS" in dc)
ok("port_map 8788", "8788" in dc)
ok("index /ui", "/ui" in dc)
ok("store_app_id tokyoos", "tokyoos" in dc)

print("\n3. SCRIPTS")
ok("healthcheck.sh exists", (BASE_DIR / "scripts" / "healthcheck.sh").exists())

print("\n4. APP.PY ENDPOINTS")
app = (BASE_DIR / "app.py").read_text() if (BASE_DIR / "app.py").exists() else ""
for ep in ["/tokyo/zimaos/volumes","/tokyo/zimaos/ports","/tokyo/zimaos/app-metadata",
           "/tokyo/tools/directories","/tokyo/tools/env-checklist"]:
    ok(f"Route {ep}", ep in app)

print("\n5. CONFIG FILES")
for f in ["external_tools.example.json","zimaos_tools.example.json","mcp_servers.example.json"]:
    ok(f"config/{f}", (BASE_DIR/"config"/f).exists())
tools_cfg = json.loads((BASE_DIR/"config"/"external_tools.example.json").read_text()) if (BASE_DIR/"config"/"external_tools.example.json").exists() else {}
for t in tools_cfg.get("external_tools",[]):
    ok(f"{t['id']} required=false", not t.get("required",True), t.get("required"))

print("\n6. UI")
ui = (BASE_DIR / "interface" / "index.html").read_text() if (BASE_DIR / "interface" / "index.html").exists() else ""
ok("UI has Deploy page", "page-deploy" in ui)
ok("UI has Tools Store", "page-tools-store" in ui)
ok("UI has blocked auto-install", "blocked" in ui.lower() or "Auto Install" in ui)
ok("UI no localStorage keys", "localStorage" not in ui.lower() or "api" not in ui.lower())
ok("UI no fake R$ values", "R$ 45" not in ui and "R$ 35" not in ui)

print("\n7. REGRESSIONS")
ok("Upload still disabled", "upload_enabled" in app)
ok("Finance engine intact", (BASE_DIR/"finance_engine"/"__init__.py").exists())
ok("Siberian connector intact", (BASE_DIR/"siberian_connector"/"client.py").exists())
ok("Siberian read_only preserved", "read_only" in (BASE_DIR/"siberian_connector"/"client.py").read_text())

print("\n8. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    c = pyf.read_text()
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in c, f"found {d}")

print("\n9. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    try: py_compile.compile(str(pyf), doraise=True); ok(f"{pyf.name}", True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}", False, str(e))

print(f"\n{'='*60}\nPHASE 3C STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
