#!/usr/bin/env python3
"""
TokyoOS Voice E2E Test — Manual Script
Guides the user through a real voice test.
No secrets exposed. No audio recorded.
"""
import sys, os, json, urllib.request
from pathlib import Path

BASE = os.getenv("TOKYO_BASE_URL", "http://localhost:8788")

def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=10).read())

def post(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(), method="POST",
                                  headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

print("=" * 55)
print("TokyoOS Voice E2E Test")
print("=" * 55)
print()

print("[1] Checking system health...")
h = get("/tokyo/system/health")
print(f"    Health: {h['health']}")

print("[2] Checking LiveKit + Gemini config...")
ts = get("/tokyo/voice/e2e/troubleshoot")
print(f"    Status: {ts['overall_status']}")
if ts["failures"]:
    for f in ts["failures"]:
        print(f"    FAIL: {f}")
    print(f"    Fix: {ts['recommended_fix']}")
    sys.exit(1)

print("[3] Creating voice session...")
s = post("/tokyo/voice/session/create", {"identity": "tokyo-user"})
room = s.get("room", "")
print(f"    Room: {room}")
print(f"    Status: {s['status']}")

print("[4] Starting E2E test mode...")
post("/tokyo/voice/e2e/start-test", {})

print()
print("=" * 55)
print("MANUAL STEPS (execute in browser):")
print("=" * 55)
print()
print(f"  1. Open: {BASE}/ui")
print("  2. Click 'Voz' in sidebar")
print("  3. Click 'Iniciar Sessao'")
print("  4. Click 'Ligar Mic' (allow microphone)")
print("  5. Click 'Iniciar Agente' (confirm START_TOKYO_AGENT)")
print(f"     Room: {room}")
print("  6. Speak: 'Tokyo, teste de voz'")
print("  7. Tokyo should respond via voice")
print()
print("  Optional: Start agent from terminal:")
print(f"    python scripts/run_tokyo_voice_agent.py --room {room}")
print()
print("Press Enter when done speaking, or Ctrl+C to abort.")
input()

print()
print("[5] Checking E2E status...")
e2e = get("/tokyo/voice/e2e/status")
steps = e2e["e2e"].get("steps", {})
criteria = e2e["e2e"].get("criteria", [])
for c in criteria:
    ok = steps.get(c, False)
    print(f"    [{'PASS' if ok else 'FAIL'}] {c}")

print()
completed = e2e["e2e"]["completed"]
total = e2e["e2e"]["total"]
print(f"Status: {completed}/{total} criteria met")
if steps.get("audio_playback_started") and steps.get("remote_audio_received"):
    print("RESULT: Tokyo spoke successfully!")
elif steps.get("agent_worker_running") and steps.get("browser_connected"):
    print("RESULT: PARTIAL — session active but audio not received")
    print("  Check: agent joined room? Gemini connected? Browser autoplay?")
else:
    print("RESULT: BLOCKED — check troubleshooting")
    ts2 = get("/tokyo/voice/e2e/troubleshoot")
    print(f"  Diagnosis: {ts2['probable_cause']}")

post("/tokyo/voice/e2e/stop-test", {})
print("\nDone.")
