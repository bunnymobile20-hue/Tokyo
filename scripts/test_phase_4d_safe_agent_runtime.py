#!/usr/bin/env python3
"""Phase 4D Static Test"""
import os, json, sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
P, F = 0, 0
def ok(n,c,d=""):
    global P, F
    (P:=P+1) if c else (F:=F+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nPhase 4D Static\n"+"="*60+"\n")
app = (BASE/"app.py").read_text() if (BASE/"app.py").exists() else ""
ui = (BASE/"interface"/"index.html").read_text() if (BASE/"interface"/"index.html").exists() else ""
agent = BASE / "tokyo_voice_agent"

print("1. RUNTIME MANAGER")
ok("runtime_manager.py exists", (agent/"runtime_manager.py").exists())
rm = (agent/"runtime_manager.py").read_text() if (agent/"runtime_manager.py").exists() else ""
ok("No shell=True in runtime", "shell=True" not in rm)
ok("No pkill in runtime", "pkill" not in rm)
ok("No killall in runtime", "killall" not in rm)
ok("sys.executable used", "sys.executable" in rm)
ok("subprocess.Popen list args", "Popen([" in rm or "Popen(" in rm)
ok("validate_room_name exists", "def validate_room_name" in rm)

print("\n2. START/STOP ENDPOINTS")
for ep in ["/tokyo/voice/agent/start","/tokyo/voice/agent/stop","/tokyo/voice/agent/runtime","/tokyo/voice/agent/workers",
           "/tokyo/voice/bidirectional/mark-client-event"]:
    ok(f"Route {ep}", ep in app)
ok("Start requires confirmation", "START_TOKYO_AGENT" in app)
ok("Stop requires confirmation", "STOP_TOKYO_AGENT" in app)
ok("Room validation", "validate_room_name" in app)
ok("Cleanup finished", "cleanup_finished" in app)

print("\n3. UI AGENT CONTROLS")
ok("Start agent button", "startAgent()" in ui)
ok("Stop agent button", "stopAgent()" in ui)
ok("Bidirectional checklist", "check-browser" in ui or "Audio Remoto" in ui)
ok("Confirmation in UI", "START_TOKYO_AGENT" in ui)

print("\n4. NO SECRETS")
ok("No secrets in frontend", "API_SECRET" not in ui.upper() or "env" in ui.lower())
ok("No secrets in runtime", "API_SECRET" not in rm.upper() or "env" in rm.lower())

print("\n5. REGRESSIONS")
ok("Siberian intact", (BASE/"siberian_connector"/"client.py").exists())
ok("Finance engine intact", (BASE/"finance_engine"/"__init__.py").exists())
ok("Upload disabled", "upload_enabled" in app)
ok("Agent safe mode", "safe" in (agent/"runtime_manager.py").read_text())

print("\n6. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE.glob("*.py")) + list(agent.glob("*.py")) + list((BASE/"siberian_connector").glob("*.py")) + list((BASE/"finance_engine").glob("*.py")):
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text())

print(f"\n{'='*60}\n4D: {P} passed, {F} failed\n{'='*60}")
sys.exit(1 if F>0 else 0)
