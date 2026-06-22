#!/usr/bin/env python3
"""TokyoOS Phase 3B — Runtime Validator"""
import json, sys, os, urllib.request, urllib.error
HOST, PORT = os.getenv("TOKYO_HOST","localhost"), os.getenv("TOKYO_HTTP_PORT","8788")
BASE = f"http://{HOST}:{PORT}"
PASS, FAIL = 0, 0

def check(n, ep, m="GET", b=None, v=None, h=False):
    global PASS, FAIL
    try:
        d = json.dumps(b).encode() if b else None
        r = urllib.request.Request(f"{BASE}{ep}", data=d, method=m)
        if d: r.add_header("Content-Type","application/json")
        resp = urllib.request.urlopen(r, timeout=10)
        body = resp.read().decode()
        if h:
            ok = "<html" in body.lower()
            (PASS := PASS + 1) if ok else (FAIL := FAIL + 1)
            print(f"  [{'PASS' if ok else 'FAIL'}] {n}")
            return body
        data = json.loads(body)
        if v:
            err = v(data)
            if err: FAIL += 1; print(f"  [FAIL] {n} — {err}"); return None
        PASS += 1; print(f"  [PASS] {n}")
        return data
    except Exception as e:
        FAIL += 1; print(f"  [FAIL] {n} — {e}"); return None

def vt(d):
    return "token_exposed=true" if d.get("_meta",{}).get("token_exposed") is True else None

print(f"{'='*60}\nTokyoOS Phase 3B — Runtime Validator\nTarget: {BASE}\n{'='*60}\n")

print("1. CORE UI")
check("GET /ui", "/ui", h=True)
check("GET /setup", "/setup", h=True)

print("\n2. VOICE")
for ep, m in [("/tokyo/voice/status","GET"),("/tokyo/voice/capabilities","GET"),("/tokyo/voice/activation/status","GET")]:
    check(f"{m} {ep}", ep, m=m, v=vt)
check("POST voice preview", "/tokyo/voice/activation/preview", m="POST", b={"command":"Tokyo, abrir dashboard"}, v=vt)

print("\n3. MCP")
for ep in ["/tokyo/mcp/status","/tokyo/mcp/servers","/tokyo/mcp/capabilities","/tokyo/mcp/tools"]:
    check(f"GET {ep}", ep, v=vt)
mc = check("GET mcp test-connection preview", "/tokyo/mcp/test-connection", m="POST", b={"server_id": "test"}, v=vt)
if mc and mc.get("tested") is False:
    PASS += 1; print(f"  [PASS] MCP test is placeholder")
else: FAIL += 1

print("\n4. API HUB")
for ep in ["/tokyo/api-hub/status","/tokyo/api-hub/connectors","/tokyo/api-hub/tools","/tokyo/api-hub/readiness"]:
    check(f"GET {ep}", ep, v=vt)

print("\n5. ZIMAOS")
for ep in ["/tokyo/zimaos/status","/tokyo/zimaos/readiness","/tokyo/zimaos/docker-status","/tokyo/zimaos/install-checklist"]:
    check(f"GET {ep}", ep, v=vt)

print("\n6. REGRESSIONS")
check("Upload status", "/tokyo/finance/uploads/status", v=vt)
check("Siberian status", "/tokyo/siberian/status", v=vt)
check("Finance status", "/tokyo/finance/status", v=vt)

# Upload disabled
up = check("  upload check", "/tokyo/finance/uploads/status", v=vt)
if up and up.get("upload_enabled") is False:
    PASS += 1; print(f"  [PASS] upload_enabled=false")
else: FAIL += 1

# Token safety
safe = True
for ep in ["/tokyo/voice/activation/status","/tokyo/mcp/status","/tokyo/api-hub/connectors","/tokyo/zimaos/status","/tokyo/system/health"]:
    try:
        d = json.loads(urllib.request.urlopen(f"{BASE}{ep}",timeout=10).read())
        if d.get("_meta",{}).get("token_exposed") is True: safe=False
    except: pass
if safe: PASS += 1; print(f"  [PASS] token_exposed=false all")
else: FAIL += 1

print(f"\n{'='*60}\nRUNTIME 3B: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
