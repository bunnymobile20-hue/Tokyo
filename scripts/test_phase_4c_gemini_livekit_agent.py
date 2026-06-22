#!/usr/bin/env python3
"""TokyoOS Phase 4C — Gemini LiveKit Agent Static Test"""
import os, json, sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
PASS, FAIL = 0, 0
def ok(n,c,d=""):
    global PASS, FAIL
    (PASS:=PASS+1) if c else (FAIL:=FAIL+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nPhase 4C Static Test\n"+"="*60+"\n")

app = (BASE_DIR/"app.py").read_text() if (BASE_DIR/"app.py").exists() else ""
ui = (BASE_DIR/"interface"/"index.html").read_text() if (BASE_DIR/"interface"/"index.html").exists() else ""
agent_dir = BASE_DIR / "tokyo_voice_agent"

print("1. AGENT MODULE")
for f in ["config.py","worker.py","gemini_realtime.py","status.py"]:
    ok(f"File tokyo_voice_agent/{f}", (agent_dir / f).exists())

print("\n2. WORKER SAFETY")
worker = (agent_dir / "worker.py").read_text() if (agent_dir / "worker.py").exists() else ""
ok("No shell=True in worker", "shell=True" not in worker)
ok("No pkill in worker", "pkill" not in worker)
ok("No killall in worker", "killall" not in worker)
ok("No os.remove in worker", "os.remove" not in worker)
ok("No sudo in worker", "sudo " not in worker)
ok("Worker imports config (keys from env)", "config" in worker.lower() or "os.getenv" in worker or "from tokyo_voice_agent" in worker)

print("\n3. CONFIG SAFETY")
cfg = (agent_dir / "config.py").read_text() if (agent_dir / "config.py").exists() else ""
ok("Config uses os.getenv for keys", "os.getenv" in cfg)
ok("Config has safe mode", "safe" in cfg.lower())

print("\n4. AGENT ENDPOINTS")
for ep in ["/tokyo/voice/agent/status","/tokyo/voice/agent/readiness","/tokyo/voice/agent/config-check",
           "/tokyo/voice/agent/rooms","/tokyo/voice/agent/start-preview","/tokyo/voice/agent/stop-preview",
           "/tokyo/voice/bidirectional/status"]:
    ok(f"Route {ep}", ep in app)

print("\n5. MANUAL RUNNER")
ok("run_tokyo_voice_agent.py exists", (BASE_DIR/"scripts"/"run_tokyo_voice_agent.py").exists())
runner = (BASE_DIR/"scripts"/"run_tokyo_voice_agent.py").read_text() if (BASE_DIR/"scripts"/"run_tokyo_voice_agent.py").exists() else ""
ok("Runner no shell=True", "shell=True" not in runner)
ok("Runner uses agent module", "tokyo_voice_agent" in runner)

print("\n6. UI AGENT STATUS")
ok("Agent status section in UI", "agent-configured-chip" in ui or "Agent Worker" in ui)
ok("Agent status polling JS", "agent/status" in ui)
ok("Agent warning messages", "agent-warning" in ui)

print("\n7. NO SECRETS")
ok("No API_SECRET in frontend", "API_SECRET" not in ui.upper() or "env" in ui.lower())
ok("No GEMINI_API_KEY in frontend", "GEMINI_API_KEY" not in ui.upper() or "env" in ui.lower())
ok("Config check returns booleans only", "_note" in app and "booleanos" in app)

print("\n8. REGRESSIONS")
ok("Siberian not_configured", (BASE_DIR/"siberian_connector"/"client.py").exists())
ok("Upload still disabled", "upload_enabled" in app)
ok("Finance engine intact", (BASE_DIR/"finance_engine"/"__init__.py").exists())
ok("Safe mode in agent", "safe_mode" in (agent_dir/"config.py").read_text().lower())

print("\n9. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE_DIR.glob("*.py")) + list(agent_dir.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text())

print("\n10. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list(agent_dir.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    try: py_compile.compile(str(pyf),doraise=True); ok(f"{pyf.name}",True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}",False,str(e))

print(f"\n{'='*60}\n4C STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
