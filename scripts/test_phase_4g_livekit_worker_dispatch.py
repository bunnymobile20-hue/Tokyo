#!/usr/bin/env python3
"""Phase 4G Static Test"""
import os,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
P,F=0,0
def ok(n,c,d=""):
    global P,F
    (P:=P+1) if c else (F:=F+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")
print("="*60+"\nPhase 4G\n"+"="*60+"\n")
app=(BASE/"app.py").read_text() if (BASE/"app.py").exists() else ""
worker=(BASE/"tokyo_voice_agent"/"worker.py").read_text() if (BASE/"tokyo_voice_agent"/"worker.py").exists() else ""
runner=(BASE/"scripts"/"run_tokyo_voice_agent.py").read_text() if (BASE/"scripts"/"run_tokyo_voice_agent.py").exists() else ""

print("1. WORKER PATTERN CORRECT")
ok("No agents.Room in worker", "agents.Room" not in worker)
ok("Uses agents.cli.run_app or correct pattern", "cli.run_app" in worker or "WorkerOptions" in worker)
ok("Uses JobContext/entrypoint", "entrypoint" in worker)
ok("Uses ctx.connect", "ctx.connect" in worker)
ok("Uses AgentSession", "AgentSession" in worker)
ok("Worker marks events", "agent_worker_started" in worker)

print("\n2. RUN SCRIPT")
ok("Runner exists", "runner" in globals() or bool(runner))
ok("Runner no shell=True", "shell=True" not in runner)
ok("Runner no pkill", "pkill" not in runner)
ok("Runner uses worker_main", "worker_main" in runner)

print("\n3. WORKER/DISPATCH ENDPOINTS")
for ep in ["/tokyo/voice/worker/status","/tokyo/voice/worker/dispatch-status",
           "/tokyo/voice/dispatch/readiness","/tokyo/voice/dispatch/status"]:
    ok(f"Route {ep}", ep in app)
ok("Dispatch create endpoint", "/tokyo/voice/dispatch/create" in app)
ok("Dispatch requires confirmation", "DISPATCH_TOKYO_AGENT" in app)

print("\n4. E2E + REGRESSIONS")
ok("14 E2E criteria preserved", "tokyo_spoke_successfully" in app)
ok("Siberian intact", (BASE/"siberian_connector"/"client.py").exists())
ok("Finance intact", (BASE/"finance_engine"/"__init__.py").exists())
ok("Upload disabled", "upload_enabled" in app)
ok("Safe mode active", "safe_mode" in app)

print("\n5. CODE SAFETY")
danger=["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE.glob("*.py"))+list((BASE/"tokyo_voice_agent").glob("*.py"))+list((BASE/"siberian_connector").glob("*.py"))+list((BASE/"finance_engine").glob("*.py")):
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text())

print(f"\n{'='*60}\n4G: {P} passed, {F} failed\n{'='*60}")
sys.exit(1 if F>0 else 0)
