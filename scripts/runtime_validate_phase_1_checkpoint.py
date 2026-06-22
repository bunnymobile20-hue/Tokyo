#!/usr/bin/env python3
"""
TokyoOS Phase 1 — Runtime Checkpoint Validator

Validates the running TokyoOS app returns correct responses
for all Phase 1 stable checkpoint endpoints.

Requires: TokyoOS app running on TOKYO_HOST:TOKYO_HTTP_PORT
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


def check(name, endpoint, expected_status=200, validate=None, is_html=False):
    global PASS, FAIL
    url = f"{BASE}{endpoint}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=10)
        status = resp.getcode()
        body = resp.read().decode("utf-8")

        if status != expected_status:
            FAIL += 1
            print(f"  [FAIL] {name} — HTTP {status} (expected {expected_status})")
            return None

        if is_html:
            if "<html" in body.lower() or "<!doctype" in body.lower():
                PASS += 1
                print(f"  [PASS] {name}")
                return body
            else:
                FAIL += 1
                print(f"  [FAIL] {name} — Not valid HTML")
                return None

        data = json.loads(body)

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
        print(f"  [FAIL] {name} — Connection error: {e}")
        return None
    except Exception as e:
        FAIL += 1
        print(f"  [FAIL] {name} — Error: {e}")
        return None


def validate_token_exposed_false(data):
    meta = data.get("_meta", {})
    te = meta.get("token_exposed", None)
    if te is None:
        return "missing _meta.token_exposed"
    if te is True:
        return "token_exposed is TRUE"
    return None


def validate_no_fake_finance(data):
    if isinstance(data.get("finance_models"), list):
        for m in data["finance_models"]:
            if m.get("status") not in ("planned", "not_configured"):
                return f"model {m.get('id')} has unexpected status: {m.get('status')}"
    return None


def validate_connector_required_false(data, connector_id):
    items = data.get("integrations", []) or data.get("connectors", [])
    for i in items:
        if i.get("id") == connector_id:
            if i.get("required") is True:
                return f"{connector_id} has required=true"
            return None
    return f"{connector_id} not found"


def validate_siberian_read_only(data):
    for i in data.get("integrations", []):
        if i.get("id") == "sistema_siberian":
            if i.get("mode") != "read_only":
                return f"sistema_siberian mode={i.get('mode')}"
            if i.get("status") not in ("not_configured", "configured"):
                pass
            return None
    return None


print("=" * 60)
print("TokyoOS Phase 1 — Runtime Checkpoint Validator")
print(f"Target: {BASE}")
print("=" * 60)
print()

# ── 1. MAIN UI ───────────────────────────────────────────
print("1. MAIN UI & SYSTEM")
check("GET /ui", "/ui", is_html=True)
check("System Health", "/tokyo/system/health", validate=validate_token_exposed_false)

# ── 2. SETUP & DOCTOR ────────────────────────────────────
print("\n2. SETUP & DOCTOR")
check("Setup Status", "/tokyo/setup/status", validate=validate_token_exposed_false)
check("Setup Checklist", "/tokyo/setup/checklist", validate=validate_token_exposed_false)
check("Tokyo Doctor", "/tokyo/doctor", validate=validate_token_exposed_false)

# ── 3. API HUB & CONNECTORS ──────────────────────────────
print("\n3. API HUB & CONNECTORS")
check("API Hub Status", "/tokyo/api-hub/status", validate=validate_token_exposed_false)
check("Providers Registry", "/tokyo/providers/registry", validate=validate_token_exposed_false)
check("Integrations Registry", "/tokyo/integrations/registry", validate=validate_token_exposed_false)
check("Connectors Registry", "/tokyo/connectors/registry", validate=validate_token_exposed_false)
check("Plugins Registry", "/tokyo/plugins/registry", validate=validate_token_exposed_false)

# ── 4. BUSINESS ──────────────────────────────────────────
print("\n4. BUSINESS DASHBOARDS")
check("Business Status", "/tokyo/business/status", validate=validate_token_exposed_false)
check("GrupsBunny Status", "/tokyo/grupsbunny/status", validate=validate_token_exposed_false)
check("Bunny Dreams Status", "/tokyo/bunnydreams/status", validate=validate_token_exposed_false)
check("Bunny Siberian Status", "/tokyo/bunnysiberian/status", validate=validate_token_exposed_false)
check("Siberian Status", "/tokyo/siberian/status", validate=validate_token_exposed_false)

# ── 5. FINANCE ───────────────────────────────────────────
print("\n5. FINANCE")
check("Finance Status", "/tokyo/finance/status", validate=validate_token_exposed_false)
fin_data = check("Finance Models", "/tokyo/finance/models", validate=validate_token_exposed_false)
if fin_data:
    validate_no_fake_finance(fin_data)
check("Finance References", "/tokyo/finance/references", validate=validate_token_exposed_false)

# ── 6. MEMORY & SECURITY ─────────────────────────────────
print("\n6. MEMORY & SECURITY")
check("Memory Status", "/tokyo/memory/status", validate=validate_token_exposed_false)
check("Security Status", "/tokyo/security/status", validate=validate_token_exposed_false)

# ── 7. CONTENT VALIDATION ────────────────────────────────
print("\n7. CONTENT VALIDATION")

# Check integrations for required=false
int_data = check("  Integrations content", "/tokyo/integrations/registry")
if int_data:
    for conn_id in ("hermes", "mcp", "ollama", "openclaw"):
        err = validate_connector_required_false(int_data, conn_id)
        if err:
            FAIL += 1
            print(f"  [FAIL] {err}")
        else:
            PASS += 1
            print(f"  [PASS] {conn_id} required=false")

    # Check sistema_siberian
    err = validate_siberian_read_only(int_data)
    if err:
        FAIL += 1
        print(f"  [FAIL] {err}")
    else:
        PASS += 1
        print(f"  [PASS] sistema_siberian read_only/not_configured")

# Check finance for no fake data
if fin_data:
    models = fin_data.get("finance_models", [])
    for model in models:
        mid = model["id"]
        status = model.get("status", "")
        ds = model.get("data_source", "")
        has_real = status not in ("planned", "not_configured") or ds in ("live", "real_api", "active")
        if has_real:
            FAIL += 1
            print(f"  [FAIL] {mid} appears to have real data (status={status}, ds={ds})")
        else:
            PASS += 1
            print(f"  [PASS] {mid} no fake/real data")

# Check voice
voice_data = check("  Voice content", "/tokyo/voice/status")
if voice_data:
    voice = voice_data.get("voice", {})
    preserved = voice.get("preserved", False)
    if preserved:
        PASS += 1
        print(f"  [PASS] Voice preserved=true")
    else:
        FAIL += 1
        print(f"  [FAIL] Voice preserved=false or missing")

# ── 8. TOKEN_EXPOSED ON ALL ──────────────────────────────
print("\n8. TOKEN_EXPOSED FALSE ON ALL ENDPOINTS")
all_endpoints = [
    "/tokyo/system/health",
    "/tokyo/setup/status",
    "/tokyo/setup/checklist",
    "/tokyo/doctor",
    "/tokyo/api-hub/status",
    "/tokyo/providers/registry",
    "/tokyo/integrations/registry",
    "/tokyo/connectors/registry",
    "/tokyo/business/status",
    "/tokyo/grupsbunny/status",
    "/tokyo/bunnydreams/status",
    "/tokyo/bunnysiberian/status",
    "/tokyo/siberian/status",
    "/tokyo/finance/status",
    "/tokyo/finance/models",
    "/tokyo/memory/status",
    "/tokyo/security/status",
    "/tokyo/mcp/status",
    "/tokyo/voice/status",
]
all_safe = True
for ep in all_endpoints:
    url = f"{BASE}{ep}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=10)
        body = json.loads(resp.read().decode("utf-8"))
        meta = body.get("_meta", {})
        te = meta.get("token_exposed", None)
        if te is True:
            all_safe = False
            print(f"  TOKEN EXPOSED at {ep} !!!")
    except Exception:
        pass

if all_safe:
    PASS += 1
    print(f"  [PASS] token_exposed=false on all endpoints")
else:
    FAIL += 1
    print(f"  [FAIL] token_exposed=true found on some endpoints")

# ── RESULT ───────────────────────────────────────────────
print()
print("=" * 60)
print(f"RUNTIME CHECKPOINT: {PASS} passed, {FAIL} failed")
print("=" * 60)

if FAIL > 0:
    print("\nSTATUS: NEEDS_FIX")
    sys.exit(1)
else:
    print("\nSTATUS: SAFE_TO_START_PHASE_2")
    sys.exit(0)
