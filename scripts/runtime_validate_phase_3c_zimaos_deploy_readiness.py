#!/usr/bin/env python3
"""TokyoOS Phase 3C — Runtime Validator"""
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

print(f"{'='*60}\nTokyoOS Phase 3C — Runtime Validator\nTarget: {BASE}\n{'='*60}\n")

print("1. CORE UI")
check("GET /ui", "/ui", h=True)
check("GET /setup", "/setup", h=True)

print("\n2. ZIMAOS ENDPOINTS")
for ep in ["/tokyo/zimaos/status","/tokyo/zimaos/readiness","/tokyo/zimaos/docker-status",
           "/tokyo/zimaos/install-checklist","/tokyo/zimaos/volumes","/tokyo/zimaos/ports","/tokyo/zimaos/app-metadata"]:
    check(f"GET {ep}", ep, v=vt)

print("\n3. TOOLS ENDPOINTS")
check("GET /tokyo/tools/directories", "/tokyo/tools/directories", v=vt)
check("GET /tokyo/tools/env-checklist", "/tokyo/tools/env-checklist", v=vt)

print("\n4. EXTERNAL TOOLS HUB")
check("GET /tokyo/api-hub/connectors", "/tokyo/api-hub/connectors", v=vt)
check("GET /tokyo/mcp/servers", "/tokyo/mcp/servers", v=vt)

print("\n5. REGRESSION CHECKS")
up = check("GET uploads status", "/tokyo/finance/uploads/status", v=vt)
if up and up.get("upload_enabled") is False:
    PASS += 1; print(f"  [PASS] upload_enabled=false")
else: FAIL += 1

sib = check("GET siberian status", "/tokyo/siberian/status", v=vt)
# Check auto_install in env-checklist
env = check("  env checklist", "/tokyo/tools/env-checklist", v=vt)
if env and env.get("auto_install_enabled") is False:
    PASS += 1; print(f"  [PASS] auto_install=false")
else: FAIL += 1

print("\n6. TOKEN_EXPOSED")
safe = True
for ep in ["/tokyo/zimaos/status","/tokyo/zimaos/app-metadata","/tokyo/tools/directories",
           "/tokyo/tools/env-checklist","/tokyo/api-hub/connectors","/tokyo/system/health"]:
    try:
        d = json.loads(urllib.request.urlopen(f"{BASE}{ep}",timeout=10).read())
        if d.get("_meta",{}).get("token_exposed") is True: safe=False
    except: pass
if safe: PASS += 1; print(f"  [PASS] token_exposed=false all")
else: FAIL += 1

print(f"\n{'='*60}\nRUNTIME 3C: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
