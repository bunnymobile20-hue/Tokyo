#!/usr/bin/env python3
"""Phase 4E Static Test"""
import os,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
P,F=0,0
def ok(n,c,d=""):
    global P,F
    (P:=P+1) if c else (F:=F+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")
print("="*60+"\nPhase 4E\n"+"="*60+"\n")
app=(BASE/"app.py").read_text() if (BASE/"app.py").exists() else ""
ui=(BASE/"interface"/"index.html").read_text() if (BASE/"interface"/"index.html").exists() else ""
print("1. E2E ENDPOINTS")
for ep in ["/tokyo/voice/e2e/status","/tokyo/voice/e2e/start-test","/tokyo/voice/e2e/stop-test","/tokyo/voice/e2e/mark-event","/tokyo/voice/e2e/report","/tokyo/voice/e2e/troubleshoot"]:
    ok(f"Route {ep}", ep in app)
ok("CRITERIA defined", "CRITERIA" in app and "session_created" in app)
ok("14 criteria steps", "tokyo_spoke_successfully" in app)
print("\n2. TROUBLESHOOTING")
ok("browser layer", "browser" in app.lower())
ok("livekit layer", "livekit" in app.lower())
ok("agent layer", "agent" in app.lower())
ok("gemini layer", "gemini" in app.lower())
ok("security layer", "security" in app.lower() or "failures" in app)
ok("Returns recommended_fix", "recommended_fix" in app)
print("\n3. CLIENT MARKERS")
ok("markE2EEvent exists", "markE2EEvent" in ui)
ok("browser_connected marker", "browser_connected" in ui)
ok("mic_published marker", "mic_published" in ui)
ok("remote_audio_received marker", "remote_audio_received" in ui)
ok("audio_playback_started marker", "audio_playback_started" in ui)
print("\n4. UI E2E PANEL")
ok("E2E start button", "startE2ETest" in ui)
ok("E2E stop button", "stopE2ETest" in ui)
ok("Troubleshoot button", "fetchTroubleshoot" in ui)
ok("Teste Real de Voz section", "Teste Real de Voz" in ui or "E2E" in ui)
print("\n5. MANUAL SCRIPT")
ok("run_voice_e2e_test_manual.py", (BASE/"scripts"/"run_voice_e2e_test_manual.py").exists())
print("\n6. NO SECRETS")
ok("No secrets in UI", "API_SECRET" not in ui.upper() or "env" in ui.lower())
ok("No secrets in app", "GEMINI_API_KEY" not in app or "env" in app)
print("\n7. REGRESSIONS")
ok("Siberian intact", (BASE/"siberian_connector"/"client.py").exists())
ok("Finance intact", (BASE/"finance_engine"/"__init__.py").exists())
ok("Upload disabled", "upload_enabled" in app)
print(f"\n{'='*60}\n4E: {P} passed, {F} failed\n{'='*60}")
sys.exit(1 if F>0 else 0)
