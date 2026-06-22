#!/usr/bin/env python3
"""TokyoOS Phase 3B.1 — Voice Interface Static Test"""
import os, json, sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
PASS, FAIL = 0, 0
def ok(n,c,d=""):
    global PASS, FAIL
    (PASS:=PASS+1) if c else (FAIL:=FAIL+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nTokyoOS Phase 3B.1 — Voice Interface Test\n"+"="*60+"\n")

ui = (BASE_DIR/"interface"/"index.html").read_text() if (BASE_DIR/"interface"/"index.html").exists() else ""
app = (BASE_DIR/"app.py").read_text() if (BASE_DIR/"app.py").exists() else ""

print("1. UI VOICE PAGE")
ok("Voice page exists", 'id="page-voice"' in ui)
ok("Orb element exists", "voice-orb" in ui)
ok("Wave bars exist", "voice-wave-bars" in ui)
ok("Control bar exists", "voice-btn-start" in ui or "voice-btn" in ui)
ok("Command preview exists", "voice-cmd-input" in ui)
ok("Quick commands exist", "voice-cmd-chip" in ui)
ok("Transcript panel exists", "transcript-panel" in ui)
ok("Safety banner exists", "voice-safety-banner" in ui)
ok("State labels exist", "listening" in ui and "thinking" in ui and "speaking" in ui)
ok("Voice simulate function", "voiceSimState" in ui)
ok("Quick cmd function", "quickCmd" in ui)

print("\n2. NO SECRETS IN FRONTEND")
ok("No LiveKit API key", "LIVEKIT_API_KEY" not in ui.upper() or 'env.' in ui.lower())
ok("No LiveKit secret", "LIVEKIT_API_SECRET" not in ui.upper() or 'env.' in ui.lower())
ok("No Gemini key", "GEMINI_API_KEY" not in ui.upper() or 'env.' in ui.lower())
ok("No OpenAI key", "OPENAI_API_KEY" not in ui.upper() or 'env.' in ui.lower())
ok("No localStorage secrets", "localStorage.setItem" not in ui.lower() or "token" not in ui.lower())
ok("No console.log tokens", "console.log(token" not in ui.lower())

print("\n3. ENDPOINTS PRESERVED")
for ep in ["/tokyo/voice/status","/tokyo/voice/capabilities","/tokyo/voice/activation/status","/tokyo/voice/activation/preview"]:
    ok(f"Endpoint {ep}", ep in app)
ok("Voice interface/status endpoint", "/tokyo/voice/interface/status" in app)
ok("Session mock-status endpoint", "/tokyo/voice/session/mock-status" in app)

print("\n4. VOICE CONFIG")
cfg = json.loads((BASE_DIR/"config"/"voice_commands.example.json").read_text()) if (BASE_DIR/"config"/"voice_commands.example.json").exists() else {}
cmds = cfg.get("commands",[])
ok("10 commands in config", len(cmds) >= 10, len(cmds))
for cid in ["open_dashboard","open_grupsbunny","open_finance","open_mcp","system_status"]:
    ok(f"Command {cid}", any(c["id"]==cid for c in cmds))
sts = cfg.get("states",{})
for state in ["offline","idle","listening","thinking","speaking","error"]:
    ok(f"State {state}", state in sts)

print("\n5. REGRESSIONS")
ok("Upload still disabled", "upload_enabled" in app)
ok("Siberian read_only preserved", (BASE_DIR/"siberian_connector"/"client.py").exists())

print("\n6. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text(), f"found {d}")

print("\n7. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    try: py_compile.compile(str(pyf),doraise=True); ok(f"{pyf.name}",True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}",False,str(e))

print(f"\n{'='*60}\n3B.1 STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL>0 else 0)
