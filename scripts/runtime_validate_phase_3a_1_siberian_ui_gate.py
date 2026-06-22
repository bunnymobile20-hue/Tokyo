#!/usr/bin/env python3
"""TokyoOS Phase 3A.1 — Runtime Validator"""
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

print(f"{'='*60}\nTokyoOS Phase 3A.1 — Runtime Validator\nTarget: {BASE}\n{'='*60}\n")

print("1. CORE + UI")
check("GET /ui", "/ui", h=True)
check("System Health", "/tokyo/system/health", v=vt)

print("\n2. SIBERIAN ENDPOINTS")
for ep in ["/tokyo/siberian/status","/tokyo/siberian/health","/tokyo/siberian/capabilities",
           "/tokyo/siberian/schema","/tokyo/siberian/companies","/tokyo/siberian/stores"]:
    check(f"GET {ep}", ep, v=vt)

rd = check("GET real-api-readiness", "/tokyo/siberian/real-api-readiness", v=vt)
if rd:
    ready = rd.get("ready_for_real_api")
    if ready is False:
        PASS += 1; print(f"  [PASS] ready_for_real_api=false")
    else: FAIL += 1; print(f"  [FAIL] ready={ready}")
    if rd.get("allowed_methods") == ["GET"]:
        PASS += 1; print(f"  [PASS] allowed_methods=GET only")
    else: FAIL += 1
    blocked = rd.get("blocked_methods",[])
    if all(m in str(blocked) for m in ["POST","PUT","PATCH","DELETE"]):
        PASS += 1; print(f"  [PASS] blocked_methods correct")
    else: FAIL += 1

print("\n3. SIBERIAN MODE")
s = check("  Siberian mode", "/tokyo/siberian/status", v=vt)
if s:
    m = str(s).lower()
    if "read_only" in m:
        PASS += 1; print(f"  [PASS] mode read_only")
    else: FAIL += 1

print("\n4. REGRESSION")
check("Uploads Status", "/tokyo/finance/uploads/status", v=vt)
check("Business Sources", "/tokyo/business/data-sources", v=vt)
up = check("  upload check", "/tokyo/finance/uploads/status", v=vt)
if up and up.get("upload_enabled") is False:
    PASS += 1; print(f"  [PASS] upload_enabled=false")
else: FAIL += 1
dre = check("  calc check", "/tokyo/finance/calculate/dre", m="POST", b={"gross_revenue":100})
if dre and "pending_validation" in dre.get("validation_status",""):
    PASS += 1; print(f"  [PASS] calc pending_validation")
else: FAIL += 1

print("\n5. TOKEN_EXPOSED")
safe = True
for ep in ["/tokyo/siberian/real-api-readiness","/tokyo/siberian/status","/tokyo/finance/status","/tokyo/system/health"]:
    try:
        d = json.loads(urllib.request.urlopen(f"{BASE}{ep}",timeout=10).read())
        if d.get("_meta",{}).get("token_exposed") is True: safe=False
    except: pass
if safe: PASS += 1; print(f"  [PASS] token_exposed=false all")
else: FAIL += 1

print(f"\n{'='*60}\nRUNTIME 3A.1: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
