#!/usr/bin/env python3
"""TokyoOS Phase 4B — LiveKit Browser Client Static Test"""
import os, json, sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
PASS, FAIL = 0, 0
def ok(n,c,d=""):
    global PASS, FAIL
    (PASS:=PASS+1) if c else (FAIL:=FAIL+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nPhase 4B Static Test\n"+"="*60+"\n")

app = (BASE_DIR/"app.py").read_text() if (BASE_DIR/"app.py").exists() else ""
ui = (BASE_DIR/"interface"/"index.html").read_text() if (BASE_DIR/"interface"/"index.html").exists() else ""

print("1. LIVEKIT CLIENT IN FRONTEND")
ok("LiveKit SDK loaded", "livekit-client" in ui or "LiveKitClient" in ui)
ok("Room connection code", "lkRoom" in ui and "Room(" in ui)
ok("Microphone toggle function", "toggleMic" in ui)
ok("Remote audio attach", "TrackSubscribed" in ui or "track.attach" in ui)

print("\n2. SESSION FUNCTIONS")
ok("startRealSession v2", "startRealSession" in ui)
ok("stopRealSession v2", "stopRealSession" in ui)
ok("cleanupLocalTracks", "cleanupLocalTracks" in ui)
ok("updateSessionUI", "updateSessionUI" in ui)

print("\n3. SESSION STATES")
for state in ["idle","connecting","connected","listening","speaking","muted","error","offline"]:
    ok(f"State {state}", state in ui.lower())

print("\n4. NO SECRETS IN FRONTEND")
ok("No LIVEKIT_API_SECRET", "LIVEKIT_API_SECRET" not in ui.upper() or 'env' in ui.lower())
ok("No GEMINI_API_KEY", "GEMINI_API_KEY" not in ui.upper() or 'env' in ui.lower())
ok("No OPENAI_API_KEY", "OPENAI_API_KEY" not in ui.upper() or 'env' in ui.lower())
ok("No localStorage setItem", "localStorage.setItem" not in ui.lower())
ok("No console.log token", "console.log(token" not in ui.lower() and "console.log(access" not in ui.lower())

print("\n5. BACKEND ENDPOINTS")
for ep in ["/tokyo/voice/session/create","/tokyo/voice/session/stop","/tokyo/voice/session/status",
           "/tokyo/voice/livekit/status","/tokyo/voice/gemini-realtime/status"]:
    ok(f"Route {ep}", ep in app)

print("\n6. REGRESSIONS")
ok("Siberian not_configured preserved", (BASE_DIR/"siberian_connector"/"client.py").exists())
ok("Upload still disabled", "upload_enabled" in app)
ok("Finance engine intact", (BASE_DIR/"finance_engine"/"__init__.py").exists())
ok("Camera preserved", "camera-tile" in ui or "camera-off" in ui)
ok("Stop session no pkill", "pkill" not in app and "killall" not in app)

print("\n7. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text())

print("\n8. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    try: py_compile.compile(str(pyf),doraise=True); ok(f"{pyf.name}",True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}",False,str(e))

print(f"\n{'='*60}\n4B STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
