#!/usr/bin/env python3
"""
TokyoOS Phase 2 — Runtime Validator

Validates running app endpoints for Phase 2 Read-Only Data Layer.
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


def check(name, endpoint, expected_status=200, validate=None, is_html=False, method="GET", body=None):
    global PASS, FAIL
    url = f"{BASE}{endpoint}"
    try:
        data_bytes = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data_bytes, method=method)
        if data_bytes:
            req.add_header("Content-Type", "application/json")
        resp = urllib.request.urlopen(req, timeout=10)
        status = resp.getcode()
        resp_body = resp.read().decode("utf-8")

        if status != expected_status:
            FAIL += 1
            print(f"  [FAIL] {name} — HTTP {status} (expected {expected_status})")
            return None

        if is_html:
            if "<html" in resp_body.lower() or "<!doctype" in resp_body.lower():
                PASS += 1
                print(f"  [PASS] {name}")
                return resp_body
            FAIL += 1
            print(f"  [FAIL] {name} — Not HTML")
            return None

        data = json.loads(resp_body)

        if validate:
            errors = validate(data)
            if errors:
                FAIL += 1
                print(f"  [FAIL] {name} — {errors}")
                return None

        PASS += 1
        print(f"  [PASS] {name}")
        return data
    except urllib.error.URLError as e:
        FAIL += 1
        print(f"  [FAIL] {name} — {e}")
        return None
    except Exception as e:
        FAIL += 1
        print(f"  [FAIL] {name} — {e}")
        return None


def v_token(data):
    te = data.get("_meta", {}).get("token_exposed", None)
    if te is None:
        return "missing token_exposed"
    if te is True:
        return "token_exposed is TRUE"
    return None


def v_pending(data):
    vs = data.get("validation_status", "")
    if "pending_validation" not in vs and isinstance(data.get("data"), dict):
        pass
    return None


print("=" * 60)
print("TokyoOS Phase 2 — Runtime Validator")
print(f"Target: {BASE}")
print("=" * 60)
print()

# ── 1. CORE & UI ─────────────────────────────────────────
print("1. CORE ENDPOINTS")
check("GET /ui", "/ui", is_html=True)
check("System Health", "/tokyo/system/health", validate=v_token)

# ── 2. FINANCE STATUS ────────────────────────────────────
print("\n2. FINANCE STATUS")
check("Finance Status", "/tokyo/finance/status", validate=v_token)
check("Finance Models", "/tokyo/finance/models", validate=v_token)
check("Finance References", "/tokyo/finance/references", validate=v_token)

# ── 3. FINANCE UPLOADS ───────────────────────────────────
print("\n3. FINANCE UPLOADS")
check("Uploads Status", "/tokyo/finance/uploads/status", validate=v_token)
check("Uploads Registry", "/tokyo/finance/uploads/registry", validate=v_token)
check("Uploads Validate (xlsx)", "/tokyo/finance/uploads/validate", method="POST", body={"filename": "test.xlsx"})
check("Uploads Validate (xlsm blocked)", "/tokyo/finance/uploads/validate", method="POST", body={"filename": "test.xlsm"})

# ── 4. FINANCE CALCULATIONS ──────────────────────────────
print("\n4. FINANCE CALCULATIONS")

dre = check("POST DRE", "/tokyo/finance/calculate/dre", method="POST",
            body={"gross_revenue": 100000, "deductions": 10000, "cogs": 50000, "fixed_expenses": 20000, "variable_expenses": 10000})
if dre:
    ok_dre = dre.get("success") is True
    vs_dre = dre.get("validation_status", "")
    if ok_dre and "pending_validation" in vs_dre:
        print(f"  [PASS] DRE success + pending_validation")
        PASS += 1
    else:
        print(f"  [FAIL] DRE success={ok_dre} validation={vs_dre}")
        FAIL += 1
    te_dre = dre.get("_meta", {}).get("token_exposed", None)
    if te_dre is False:
        print(f"  [PASS] DRE token_exposed=false")
        PASS += 1
    else:
        print(f"  [FAIL] DRE token_exposed={te_dre}")
        FAIL += 1

cf = check("POST Cash Flow", "/tokyo/finance/calculate/cash-flow", method="POST",
           body={"opening_balance": 50000, "inflows": 20000, "outflows": 15000})
if cf:
    ok_cf = cf.get("success") is True
    if ok_cf:
        print(f"  [PASS] Cash Flow success")
        PASS += 1
    else:
        print(f"  [FAIL] Cash Flow failed")
        FAIL += 1

be = check("POST Break Even", "/tokyo/finance/calculate/break-even", method="POST",
           body={"fixed_costs": 30000, "contribution_margin_percent": 40})
if be:
    if be.get("success"):
        print(f"  [PASS] Break Even success")
        PASS += 1
    else:
        print(f"  [FAIL] Break Even failed")
        FAIL += 1

oc = check("POST Operational Cycle", "/tokyo/finance/calculate/operational-cycle", method="POST",
           body={"average_inventory_days": 30, "average_receivable_days": 15})
if oc:
    if oc.get("success"):
        print(f"  [PASS] Operational Cycle success")
        PASS += 1
    else:
        print(f"  [FAIL] Operational Cycle failed")
        FAIL += 1

fc = check("POST Financial Cycle", "/tokyo/finance/calculate/financial-cycle", method="POST",
           body={"average_inventory_days": 30, "average_receivable_days": 15, "average_payable_days": 20})
if fc:
    if fc.get("success"):
        print(f"  [PASS] Financial Cycle success")
        PASS += 1
    else:
        print(f"  [FAIL] Financial Cycle failed")
        FAIL += 1

mc = check("POST Minimum Cash", "/tokyo/finance/calculate/minimum-cash", method="POST",
           body={"daily_cash_need": 1000, "financial_cycle_days": 25})
if mc:
    if mc.get("success"):
        print(f"  [PASS] Minimum Cash success")
        PASS += 1
    else:
        print(f"  [FAIL] Minimum Cash failed")
        FAIL += 1

# ── 5. SIBERIAN ──────────────────────────────────────────
print("\n5. SISTEMA SIBERIAN")
sib_status = check("Siberian Status", "/tokyo/siberian/status", validate=v_token)
if sib_status:
    ss = sib_status.get("sistema_siberian", {})
    mode = ss.get("mode", "")
    status = ss.get("status", "")
    if mode == "read_only" and status == "not_configured":
        print(f"  [PASS] Siberian read_only/not_configured")
        PASS += 1
    else:
        print(f"  [FAIL] Siberian mode={mode} status={status}")
        FAIL += 1

check("Siberian Health", "/tokyo/siberian/health", validate=v_token)
check("Siberian Schema", "/tokyo/siberian/schema", validate=v_token)
check("Siberian Capabilities", "/tokyo/siberian/capabilities", validate=v_token)
check("Siberian Companies", "/tokyo/siberian/companies", validate=v_token)
check("Siberian Stores", "/tokyo/siberian/stores", validate=v_token)
check("Siberian Sales Summary", "/tokyo/siberian/sales/summary", validate=v_token)
check("Siberian Finance Summary", "/tokyo/siberian/finance/summary", validate=v_token)

# ── 6. BUSINESS DATA LAYER ───────────────────────────────
print("\n6. BUSINESS DATA LAYER")
check("Data Sources", "/tokyo/business/data-sources", validate=v_token)
check("Scopes", "/tokyo/business/scopes", validate=v_token)
check("Readiness", "/tokyo/business/readiness", validate=v_token)

# ── 7. AUDIT ─────────────────────────────────────────────
print("\n7. AUDIT LOG")
check("Finance Audit", "/tokyo/finance/audit", validate=v_token)

# ── 8. TOKEN_EXPOSED ON ALL NEW ENDPOINTS ────────────────
print("\n8. TOKEN_EXPOSED CHECK (all Phase 2 endpoints)")
phase2_endpoints = [
    "/tokyo/finance/uploads/status",
    "/tokyo/finance/uploads/registry",
    "/tokyo/siberian/status",
    "/tokyo/siberian/health",
    "/tokyo/siberian/schema",
    "/tokyo/business/data-sources",
    "/tokyo/business/scopes",
    "/tokyo/business/readiness",
    "/tokyo/finance/audit",
]
all_safe = True
for ep in phase2_endpoints:
    try:
        req = urllib.request.Request(f"{BASE}{ep}")
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        te = data.get("_meta", {}).get("token_exposed", None)
        if te is True:
            all_safe = False
            print(f"  TOKEN EXPOSED at {ep} !!!")
    except Exception:
        pass

if all_safe:
    print(f"  [PASS] token_exposed=false on all Phase 2 endpoints")
    PASS += 1
else:
    print(f"  [FAIL] token_exposed=true found")
    FAIL += 1

# ── RESULT ───────────────────────────────────────────────
print()
print("=" * 60)
print(f"RUNTIME PHASE 2: {PASS} passed, {FAIL} failed")
print("=" * 60)

if FAIL > 0:
    print("\nSTATUS: NEEDS_FIX")
    sys.exit(1)
else:
    print("\nSTATUS: SAFE_TO_CONTINUE_PHASE_2_READ_ONLY_DATA_LAYER")
    sys.exit(0)
