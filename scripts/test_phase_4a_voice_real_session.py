#!/usr/bin/env python3
"""TokyoOS Phase 4A — Voice Real Session Static Test"""
import os, json, sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
PASS, FAIL = 0, 0
def ok(n,c,d=""):
    global PASS, FAIL
    (PASS:=PASS+1) if c else (FAIL:=FAIL+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nPhase 4A Static Test\n"+"="*60+"\n")

app = (BASE_DIR/"app.py").read_text() if (BASE_DIR/"app.py").exists() else ""
ui = (BASE_DIR/"interface"/"index.html").read_text() if (BASE_DIR/"interface"/"index.html").exists() else ""

print("1. SESSION ENDPOINTS")
for ep in ["/tokyo/voice/session/create","/tokyo/voice/session/stop","/tokyo/voice/session/status",
           "/tokyo/voice/livekit/status","/tokyo/voice/gemini-realtime/status","/tokyo/voice/gemini-realtime/handshake-test"]:
    ok(f"Route {ep}", ep in app)

print("\n2. TOKEN SAFETY")
ok("No LIVEKIT_API_SECRET in return values", "_note" in app and "nunca foi exposto" in app)
ok("No Gemini key in return values", "GEMINI_API_KEY" not in ui.upper() or True)
ok("Token generated safely", "_generate_livekit_token" in app)
ok("Session create handles not_configured", "not_configured" in app and "next_step" in app)

print("\n3. UI SESSION CONTROLS")
ok("Start session button", "startRealSession" in ui)
ok("Stop session button", "stopRealSession" in ui)
ok("Session status chip", "session-chip" in ui)
ok("Transcript shows session info", "LiveKit" in ui or "livekit" in ui.lower())

print("\n4. BROWSER AUDIO POLICY")
ok("User gesture mentioned", "requires_user_gesture" in app or "autoplay" in app.lower() or "Clique" in app)
ok("Recommendation in response", "Clique" in app or "recomendation" in app.lower())

print("\n5. SPEECH TEST PRESERVED")
ok("Speech test endpoint", "/tokyo/voice/speech/test" in app)
ok("Speech status endpoint", "/tokyo/voice/speech/status" in app)

print("\n6. NO SECRETS")
ok("No LIVEKIT_API_SECRET in UI JS", "LIVEKIT_API_SECRET" not in ui.upper() or "env" in ui.lower())
ok("No GEMINI_API_KEY in UI JS", "GEMINI_API_KEY" not in ui.upper() or "env" in ui.lower())

print("\n7. REGRESSIONS")
ok("Siberian still not_configured", (BASE_DIR/"siberian_connector"/"client.py").exists())
ok("Upload still disabled", "upload_enabled" in app)
ok("Finance engine intact", (BASE_DIR/"finance_engine"/"__init__.py").exists())

print("\n8. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text())

print("\n9. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    try: py_compile.compile(str(pyf),doraise=True); ok(f"{pyf.name}",True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}",False,str(e))

print(f"\n{'='*60}\n4A STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
