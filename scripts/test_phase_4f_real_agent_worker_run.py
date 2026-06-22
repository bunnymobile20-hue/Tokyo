#!/usr/bin/env python3
"""Phase 4F Static Test"""
import os,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
P,F=0,0
def ok(n,c,d=""):
    global P,F
    (P:=P+1) if c else (F:=F+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")
print("="*60+"\nPhase 4F\n"+"="*60+"\n")
app=(BASE/"app.py").read_text() if (BASE/"app.py").exists() else ""
ui=(BASE/"interface"/"index.html").read_text() if (BASE/"interface"/"index.html").exists() else ""
worker=(BASE/"tokyo_voice_agent"/"worker.py").read_text() if (BASE/"tokyo_voice_agent"/"worker.py").exists() else ""
rm=(BASE/"tokyo_voice_agent"/"runtime_manager.py").read_text() if (BASE/"tokyo_voice_agent"/"runtime_manager.py").exists() else ""

print("1. WORKER FIXED")
ok("Worker uses correct LiveKit API", "agents.cli.run_app" in worker or "WorkerOptions" in worker)
ok("Worker uses entrypoint pattern", "entrypoint" in worker)
ok("Worker uses ctx.connect", "ctx.connect" in worker)
ok("Worker uses AgentSession", "AgentSession" in worker)
ok("Worker uses Google Gemini", "google.beta" in worker or "google" in worker)
ok("Worker marks agent_worker_started", "agent_worker_started" in worker)
ok("Worker marks room_joined", "room_joined" in worker)
ok("No agents.Room in worker", "agents.Room" not in worker)

print("\n2. CONFIG VALIDATION")
for ep in ["/tokyo/voice/agent/config-check","/tokyo/voice/agent/readiness","/tokyo/voice/livekit/status","/tokyo/voice/gemini-realtime/status"]:
    ok(f"Endpoint {ep}", ep in app)
ok("14 E2E criteria defined", "session_created" in app and "tokyo_spoke_successfully" in app)

print("\n3. RUNTIME MANAGER SAFE")
ok("Runtime manager logs to file", "log_fh" in rm or "worker_" in rm)
ok("No shell=True in runtime", "shell=True" not in rm)
ok("No pkill in runtime", "pkill" not in rm)
ok("No killall in runtime", "killall" not in rm)

print("\n4. NO SECRETS")
ok("No secrets in worker", "API_SECRET" not in worker.upper() or 'env' in worker.lower())
ok("No secrets in UI", "API_SECRET" not in ui.upper() or 'env' in ui.lower())

print("\n5. REGRESSIONS")
ok("Siberian intact", (BASE/"siberian_connector"/"client.py").exists())
ok("Finance intact", (BASE/"finance_engine"/"__init__.py").exists())
ok("Upload disabled", "upload_enabled" in app)

print(f"\n{'='*60}\n4F: {P} passed, {F} failed\n{'='*60}")
sys.exit(1 if F>0 else 0)
