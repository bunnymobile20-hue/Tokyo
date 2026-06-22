#!/usr/bin/env python3
"""Phase 4I Static Test — Force Dispatch + API Keys"""
import os,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
P,F=0,0
def ok(n,c,d=""):
    global P,F
    (P:=P+1) if c else (F:=F+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")
print("="*60+"\nPhase 4I\n"+"="*60+"\n")
app=(BASE/"app.py").read_text() if (BASE/"app.py").exists() else ""
ui=(BASE/"interface"/"index.html").read_text() if (BASE/"interface"/"index.html").exists() else ""
print("1. DISPATCH MODULE")
dp=(BASE/"tokyo_voice_agent"/"dispatch.py")
ok("dispatch.py exists", dp.exists())
dp_c = dp.read_text() if dp.exists() else ""
ok("create_dispatch function", "def create_dispatch" in dp_c)
ok("Uses CreateAgentDispatchRequest", "CreateAgentDispatchRequest" in dp_c)
ok("Uses LiveKitAPI", "LiveKitAPI" in dp_c)
ok("session create with dispatch", "create_session_with_dispatch" in dp_c)
print("\n2. DISPATCH ENDPOINTS")
for ep in ["/tokyo/voice/dispatch/capability","/tokyo/voice/dispatch/create","/tokyo/voice/dispatch/latest"]:
    ok(f"Route {ep}", ep in app)
ok("Session create uses dispatch", "create_session_with_dispatch" in app)
ok("Dispatch requires confirmation", "DISPATCH_TOKYO_AGENT" in app)
print("\n3. API KEY CENTER")
ak=(BASE/"tokyo_security"/"api_keys.py")
ok("api_keys.py exists", ak.exists())
ak_c = ak.read_text() if ak.exists() else ""
ok("generate_api_key", "def generate_api_key" in ak_c)
ok("hash_api_key", "hashlib" in ak_c or "sha256" in ak_c)
ok("tkos_ prefix", "tkos_" in ak_c)
ok("verify_api_key", "def verify_api_key" in ak_c)
ok("revoke_api_key", "def revoke_api_key" in ak_c)
ok("rotate_api_key", "def rotate_api_key" in ak_c)
for ep in ["/tokyo/security/api-keys/status","/tokyo/security/api-keys","/tokyo/security/api-keys/create",
           "/tokyo/security/api-keys/revoke","/tokyo/security/api-keys/rotate","/tokyo/security/api-keys/verify"]:
    ok(f"Route {ep}", ep in app)
ok("Create requires confirmation", "CREATE_TOKYO_API_KEY" in app)
ok("Revoke requires confirmation", "REVOKE_TOKYO_API_KEY" in app)
ok("Rotate requires confirmation", "ROTATE_TOKYO_API_KEY" in app)
print("\n4. REGRESSIONS")
ok("Siberian intact", (BASE/"siberian_connector"/"client.py").exists())
ok("E2E 14 criteria", "tokyo_spoke_successfully" in app)
ok("Upload disabled", "upload_enabled" in app)
ok("Safe mode", "safe_mode" in app)
print(f"\n{'='*60}\n4I: {P} passed, {F} failed\n{'='*60}")
sys.exit(1 if F>0 else 0)
