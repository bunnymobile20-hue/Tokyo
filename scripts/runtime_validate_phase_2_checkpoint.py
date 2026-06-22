#!/usr/bin/env python3
"""
TokyoOS Phase 2 — Runtime Checkpoint Validator

Validates all Phase 2 endpoints and data integrity rules on running app.
"""

import json
import sys
import os
import urllib.request
import urllib.error

HOST = os.getenv("TOKYO_HOST", "localhost")
PORT = os.getenv("TOKYO_HTTP_PORT", "8788")
BASE = f"http://{HOST}:{PORT}"

PASS = 0
FAIL = 0

def check(name, endpoint, method="GET", body=None, expected=200, validate=None, is_html=False):
    global PASS, FAIL
    url = f"{BASE}{endpoint}"
    try:
        data_bytes = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data_bytes, method=method)
        if data_bytes:
            req.add_header("Content-Type", "application/json")
        resp = urllib.request.urlopen(req, timeout=10)
        status = resp.getcode()
        resp_body = resp.read().decode("utf-8")

        if status != expected:
            FAIL += 1
            print(f"  [FAIL] {name} — HTTP {status}")
            return None

        if is_html:
            ok_html = "<html" in resp_body.lower() or "<!doctype" in resp_body.lower()
            if ok_html:
                PASS += 1
                print(f"  [PASS] {name}")
            else:
                FAIL += 1
                print(f"  [FAIL] {name} — Not HTML")
            return resp_body

        data = json.loads(resp_body)

        if validate:
            err = validate(data)
            if err:
                FAIL += 1
                print(f"  [FAIL] {name} — {err}")
                return None

        PASS += 1
        print(f"  [PASS] {name}")
        return data
    except Exception as e:
        FAIL += 1
        print(f"  [FAIL] {name} — {e}")
        return None

def v_token(data):
    if data.get("_meta", {}).get("token_exposed") is True:
        return "token_exposed=true"
    return None

def get_all_safe():
    eps = [
        "/tokyo/system/health", "/tokyo/finance/status", "/tokyo/finance/models",
        "/tokyo/finance/uploads/status", "/tokyo/finance/uploads/registry",
        "/tokyo/siberian/status", "/tokyo/siberian/health", "/tokyo/siberian/schema",
        "/tokyo/business/data-sources", "/tokyo/business/scopes",
        "/tokyo/business/readiness", "/tokyo/finance/audit",
    ]
    for ep in eps:
        try:
            req = urllib.request.Request(f"{BASE}{ep}")
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("_meta", {}).get("token_exposed") is True:
                return False
        except Exception:
            pass
    return True

print("=" * 60)
print("TokyoOS Phase 2 — Runtime Checkpoint")
print(f"Target: {BASE}")
print("=" * 60)
print()

# ── 1. CORE ──────────────────────────────────────────────
print("1. CORE")
check("GET /ui", "/ui", is_html=True)
check("System Health", "/tokyo/system/health", validate=v_token)

# ── 2. FINANCE STATUS ────────────────────────────────────
print("\n2. FINANCE")
check("Finance Status", "/tokyo/finance/status", validate=v_token)
check("Finance Models", "/tokyo/finance/models", validate=v_token)
check("Finance References", "/tokyo/finance/references", validate=v_token)

# ── 3. UPLOADS ───────────────────────────────────────────
print("\n3. UPLOADS")
up = check("Uploads Status", "/tokyo/finance/uploads/status", validate=v_token)
if up:
    enabled = up.get("upload_enabled", None)
    if enabled is False:
        PASS += 1
        print(f"  [PASS] Upload real = false")
    else:
        FAIL += 1
        print(f"  [FAIL] Upload real = {enabled}")

check("Uploads Registry", "/tokyo/finance/uploads/registry", validate=v_token)
v = check("Uploads Validate (.xlsx)", "/tokyo/finance/uploads/validate", method="POST", body={"filename": "test.xlsx"})
if v and v.get("valid") is True:
    PASS += 1; print(f"  [PASS] .xlsx accepted")
else: FAIL += 1; print(f"  [FAIL] .xlsx not accepted")

v = check("Uploads Validate (.xlsm blocked)", "/tokyo/finance/uploads/validate", method="POST", body={"filename": "test.xlsm"})
if v and v.get("valid") is False:
    PASS += 1; print(f"  [PASS] .xlsm blocked")
else: FAIL += 1; print(f"  [FAIL] .xlsm not blocked")

# ── 4. SIBERIAN ──────────────────────────────────────────
print("\n4. SIBERIAN")
s = check("Siberian Status", "/tokyo/siberian/status", validate=v_token)
if s:
    ss = s.get("sistema_siberian", {})
    mode = ss.get("mode", "")
    status = ss.get("status", "")
    if mode == "read_only" and status == "not_configured":
        PASS += 1; print(f"  [PASS] Siberian read_only/not_configured")
    else: FAIL += 1; print(f"  [FAIL] mode={mode} status={status}")

for ep in ["/tokyo/siberian/health", "/tokyo/siberian/schema", "/tokyo/siberian/capabilities",
           "/tokyo/siberian/companies", "/tokyo/siberian/stores",
           "/tokyo/siberian/sales/summary", "/tokyo/siberian/finance/summary"]:
    check(f"Siberian {ep.split('/')[-1]}", ep, validate=v_token)

# ── 5. BUSINESS ──────────────────────────────────────────
print("\n5. BUSINESS DATA LAYER")
check("Data Sources", "/tokyo/business/data-sources", validate=v_token)
check("Scopes", "/tokyo/business/scopes", validate=v_token)
check("Readiness", "/tokyo/business/readiness", validate=v_token)

# ── 6. CALCULATIONS ──────────────────────────────────────
print("\n6. CALCULATIONS")
tests = [
    ("POST DRE", "/tokyo/finance/calculate/dre", {"gross_revenue": 10000, "deductions": 1000, "cogs": 5000}),
    ("POST Cash Flow", "/tokyo/finance/calculate/cash-flow", {"opening_balance": 500, "inflows": 200, "outflows": 150}),
    ("POST Break Even", "/tokyo/finance/calculate/break-even", {"fixed_costs": 3000, "contribution_margin_percent": 40}),
    ("POST Op Cycle", "/tokyo/finance/calculate/operational-cycle", {"average_inventory_days": 30, "average_receivable_days": 15}),
    ("POST Min Cash", "/tokyo/finance/calculate/minimum-cash", {"daily_cash_need": 100, "financial_cycle_days": 10}),
]
for name, ep, body in tests:
    r = check(name, ep, method="POST", body=body, validate=v_token)
    if r:
        vs = r.get("validation_status", "")
        if "pending_validation" in vs:
            PASS += 1; print(f"  [PASS] {name} pending_validation")
        else: FAIL += 1; print(f"  [FAIL] {name} validation={vs}")

# ── 7. AUDIT ─────────────────────────────────────────────
print("\n7. AUDIT")
check("Audit Log", "/tokyo/finance/audit", validate=v_token)

# ── 8. TOKEN_EXPOSED ─────────────────────────────────────
print("\n8. TOKEN_EXPOSED")
if get_all_safe():
    PASS += 1; print(f"  [PASS] token_exposed=false on all")
else: FAIL += 1; print(f"  [FAIL] token_exposed=true detected")

# ── RESULT ───────────────────────────────────────────────
print()
print("=" * 60)
print(f"RUNTIME PHASE 2 CHECKPOINT: {PASS} passed, {FAIL} failed")
print("=" * 60)
if FAIL > 0:
    print("\nSTATUS: NEEDS_FIX")
    sys.exit(1)
else:
    print("\nSTATUS: SAFE_TO_START_PHASE_3")
    sys.exit(0)
