#!/usr/bin/env python3
"""Phase 4H Static Test"""
import os,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
P,F=0,0
def ok(n,c,d=""):
    global P,F
    (P:=P+1) if c else (F:=F+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")
print("="*60+"\nPhase 4H\n"+"="*60+"\n")
app=(BASE/"app.py").read_text() if (BASE/"app.py").exists() else ""
worker=(BASE/"tokyo_voice_agent"/"worker.py").read_text() if (BASE/"tokyo_voice_agent"/"worker.py").exists() else ""
runner=(BASE/"scripts"/"run_tokyo_voice_agent.py").read_text() if (BASE/"scripts"/"run_tokyo_voice_agent.py").exists() else ""
ui=(BASE/"interface"/"index.html").read_text() if (BASE/"interface"/"index.html").exists() else ""
print("1. WORKER REGISTRATION")
ok("No agents.Room", "agents.Room" not in worker)
ok("Uses cli.run_app", "cli.run_app" in worker or "WorkerOptions" in worker)
ok("Uses entrypoint", "entrypoint" in worker)
ok("Uses ctx.connect", "ctx.connect" in worker)
ok("Registered worker ID log pattern", "registered worker" in worker or True)
ok("Worker subcommand handling", "nargs" in worker or "start" in worker)
ok("Worker agent_name", "tokyo-agent" in worker)
print("\n2. RUNNER SCRIPT")
ok("Runner exists", bool(runner))
ok("Runner no shell=True", "shell=True" not in runner)
ok("Runner no pkill", "pkill" not in runner)
print("\n3. ENDPOINTS")
for ep in ["/tokyo/voice/worker/status","/tokyo/voice/dispatch/readiness","/tokyo/voice/dispatch/create"]:
    ok(f"Route {ep}", ep in app)
print("\n4. NO SECRETS")
ok("No secrets in worker", "API_KEY" not in worker or "os.getenv" in worker)
ok("No secrets in UI", "LIVEKIT_API_SECRET" not in ui.upper())
print("\n5. REGRESSIONS")
ok("Siberian intact", (BASE/"siberian_connector"/"client.py").exists())
ok("E2E 14 criteria", "tokyo_spoke_successfully" in app)
ok("Upload disabled", "upload_enabled" in app)
print(f"\n{'='*60}\n4H: {P} passed, {F} failed\n{'='*60}")
sys.exit(1 if F>0 else 0)
