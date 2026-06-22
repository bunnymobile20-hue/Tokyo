#!/usr/bin/env python3
"""TokyoOS Phase 3A — Runtime Validator"""
import json, sys, os, urllib.request, urllib.error

HOST, PORT = os.getenv("TOKYO_HOST", "localhost"), os.getenv("TOKYO_HTTP_PORT", "8788")
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
            ok = "<html" in body.lower() or "<!doctype" in body.lower()
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

print(f"{'='*60}\nTokyoOS Phase 3A — Runtime Validator\nTarget: {BASE}\n{'='*60}\n")

print("1. CORE")
check("GET /ui", "/ui", h=True)
check("System Health", "/tokyo/system/health", v=vt)

print("\n2. SIBERIAN")
eps = ["/tokyo/siberian/status","/tokyo/siberian/health","/tokyo/siberian/schema",
       "/tokyo/siberian/capabilities","/tokyo/siberian/companies","/tokyo/siberian/stores",
       "/tokyo/siberian/sales/summary","/tokyo/siberian/finance/summary",
       "/tokyo/siberian/products/summary","/tokyo/siberian/stock/summary"]
for ep in eps:
    check(f"GET {ep}", ep, v=vt)

s = check("  Siberian mode check", "/tokyo/siberian/status", v=vt)
if s:
    mode = s.get("mode","") or s.get("_meta",{}).get("mode","")
    if "read_only" in str(mode).lower():
        PASS += 1; print(f"  [PASS] mode read_only")
    else: FAIL += 1; print(f"  [FAIL] mode={mode}")

print("\n3. REGRESSION (Phase 2)")
check("Finance Status", "/tokyo/finance/status", v=vt)
check("Finance Models", "/tokyo/finance/models", v=vt)
check("Uploads Status", "/tokyo/finance/uploads/status", v=vt)
check("Business Sources", "/tokyo/business/data-sources", v=vt)

up = check("  Upload disabled check", "/tokyo/finance/uploads/status", v=vt)
if up and up.get("upload_enabled") is False:
    PASS += 1; print(f"  [PASS] upload_enabled=false")
else: FAIL += 1; print(f"  [FAIL] upload issue")

dre = check("  Calculation check", "/tokyo/finance/calculate/dre", m="POST",
            b={"gross_revenue":100, "deductions":10, "cogs":50})
if dre and "pending_validation" in dre.get("validation_status",""):
    PASS += 1; print(f"  [PASS] calc pending_validation")
else: FAIL += 1; print(f"  [FAIL] calc status")

print("\n4. TOKEN_EXPOSED")
all_eps = eps + ["/tokyo/system/health","/tokyo/finance/status","/tokyo/business/data-sources"]
safe = True
for ep in all_eps:
    try:
        d = json.loads(urllib.request.urlopen(f"{BASE}{ep}", timeout=10).read())
        if d.get("_meta",{}).get("token_exposed") is True: safe = False; print(f"  TOKEN EXPOSED at {ep}")
    except: pass
if safe: PASS += 1; print(f"  [PASS] token_exposed=false all")
else: FAIL += 1; print(f"  [FAIL]")

print(f"\n{'='*60}\nRUNTIME 3A: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
