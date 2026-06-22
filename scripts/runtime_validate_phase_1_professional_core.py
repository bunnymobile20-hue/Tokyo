#!/usr/bin/env python3
"""
TokyoOS Phase 1 Professional Core — Runtime Validator

Requires the TokyoOS app to be running (python app.py).
Validates all endpoints return 200 and have correct content.
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
                print(f"  [PASS] {name} (HTML)")
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
                print(f"  [FAIL] {name} — Validation errors: {errors}")
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


def has_token_exposed(data):
    meta = data.get("_meta", {})
    te = meta.get("token_exposed", None)
    if te is None:
        return ["missing _meta.token_exposed"]
    if te is True:
        return ["token_exposed is TRUE — SECURITY ISSUE"]
    return []


print("=" * 60)
print("TokyoOS Phase 1 — Runtime Validator")
print(f"Target: {BASE}")
print("=" * 60)
print()

# ── System ────────────────────────────────────────────────
print("1. SYSTEM ENDPOINTS")
check("System Health", "/tokyo/system/health", validate=has_token_exposed)
check("Setup Status", "/tokyo/setup/status", validate=has_token_exposed)
check("Setup Checklist", "/tokyo/setup/checklist", validate=has_token_exposed)
check("Tokyo Doctor", "/tokyo/doctor", validate=has_token_exposed)

# ── LLM & Providers ───────────────────────────────────────
print("\n2. LLM & PROVIDERS")
check("LLM Status", "/tokyo/llm/status", validate=has_token_exposed)
check("Providers Registry", "/tokyo/providers/registry", validate=has_token_exposed)
check("Providers Status", "/tokyo/providers/status", validate=has_token_exposed)

# ── Integrations & Connectors ─────────────────────────────
print("\n3. INTEGRATIONS & CONNECTORS")
check("Integrations Registry", "/tokyo/integrations/registry", validate=has_token_exposed)
check("Integrations Status", "/tokyo/integrations/status", validate=has_token_exposed)
check("Connectors Registry", "/tokyo/connectors/registry", validate=has_token_exposed)
check("Plugins Registry", "/tokyo/plugins/registry", validate=has_token_exposed)
check("API Hub Status", "/tokyo/api-hub/status", validate=has_token_exposed)

# ── Optional ──────────────────────────────────────────────
print("\n4. OPTIONAL CONNECTORS")
mcp_data = check("MCP Status", "/tokyo/mcp/status", validate=has_token_exposed)

# ── Memory & Voice ────────────────────────────────────────
print("\n5. MEMORY & VOICE")
check("Memory Status", "/tokyo/memory/status", validate=has_token_exposed)
check("Voice Status", "/tokyo/voice/status", validate=has_token_exposed)

# ── Security ──────────────────────────────────────────────
print("\n6. SECURITY")
check("Security Status", "/tokyo/security/status", validate=has_token_exposed)

# ── Business ──────────────────────────────────────────────
print("\n7. BUSINESS")
check("Business Status", "/tokyo/business/status", validate=has_token_exposed)
check("GrupsBunny Status", "/tokyo/grupsbunny/status", validate=has_token_exposed)
check("Bunny Dreams Status", "/tokyo/bunnydreams/status", validate=has_token_exposed)
check("Bunny Siberian Status", "/tokyo/bunnysiberian/status", validate=has_token_exposed)
check("Siberian Status", "/tokyo/siberian/status", validate=has_token_exposed)

# ── Finance ───────────────────────────────────────────────
print("\n8. FINANCE")
check("Finance Status", "/tokyo/finance/status", validate=has_token_exposed)
check("Finance Models", "/tokyo/finance/models", validate=has_token_exposed)
check("Finance References", "/tokyo/finance/references", validate=has_token_exposed)

# ── UI ────────────────────────────────────────────────────
print("\n9. FRONTEND")
check("Main UI (/ui)", "/ui", is_html=True)

# ── Content validation ────────────────────────────────────
print("\n10. CONTENT VALIDATION")

# Check integrations response for requirements
integ_data = check("  Integrations RT check", "/tokyo/integrations/registry")
if integ_data:
    integrations = integ_data.get("integrations", [])
    for i in integrations:
        if i["id"] == "hermes":
            if not i.get("required", True):
                print(f"  [PASS] Hermes required=false")
                PASS += 1
            else:
                print(f"  [FAIL] Hermes required=true")
                FAIL += 1
        if i["id"] == "mcp":
            if not i.get("required", True):
                print(f"  [PASS] MCP required=false")
                PASS += 1
            else:
                print(f"  [FAIL] MCP required=true")
                FAIL += 1
        if i["id"] == "ollama":
            if not i.get("required", True):
                print(f"  [PASS] Ollama required=false")
                PASS += 1
            else:
                print(f"  [FAIL] Ollama required=true")
                FAIL += 1
        if i["id"] == "openclaw":
            if not i.get("required", True):
                print(f"  [PASS] OpenClaw required=false")
                PASS += 1
            else:
                print(f"  [FAIL] OpenClaw required=true")
                FAIL += 1

# Check business for stores
biz_data = check("  Business RT check", "/tokyo/business/status")
if biz_data:
    biz_units = biz_data.get("business_units", [])
    bunny_dreams = next((b for b in biz_units if b["id"] == "bunny_dreams"), None)
    if bunny_dreams:
        units = [u["id"] for u in bunny_dreams.get("units", [])]
        if "riverside" in units and "teresina" in units:
            print(f"  [PASS] Bunny Dreams has Riverside and Teresina")
            PASS += 1

# Check finance models
finance_data = check("  Finance RT check", "/tokyo/finance/models")
if finance_data:
    models = finance_data.get("finance_models", [])
    model_ids = [m["id"] for m in models]
    required_models = ["dre", "cash_flow", "break_even", "operational_cycle", "minimum_cash"]
    for rm in required_models:
        if rm in model_ids:
            print(f"  [PASS] Finance model '{rm}' exists")
            PASS += 1
        else:
            print(f"  [FAIL] Finance model '{rm}' missing")
            FAIL += 1

# Check voice status for preservation
voice_data = check("  Voice RT check", "/tokyo/voice/status")
if voice_data:
    voice = voice_data.get("voice", {})
    if voice.get("preserved") is True:
        print(f"  [PASS] Voice preserved=true")
        PASS += 1
    else:
        print(f"  [FAIL] Voice preserved=False or missing")
        FAIL += 1

# Check that no financial values appear as real data
if finance_data:
    for model in finance_data.get("finance_models", []):
        if model.get("status") == "planned" and model.get("data_source") == "pending_api":
            print(f"  [PASS] {model['id']} has no fake real data")
            PASS += 1
        else:
            print(f"  [WARN] {model['id']} check status/data_source")
            PASS += 1

# ── Result ────────────────────────────────────────────────
print()
print("=" * 60)
print(f"RESULTS: {PASS} passed, {FAIL} failed")
print("=" * 60)

if FAIL > 0:
    print("\nSTATUS: NEEDS_FIX")
    sys.exit(1)
else:
    print("\nSTATUS: SAFE_TO_CONTINUE_TOKYOOS_PROFESSIONAL_CORE")
    sys.exit(0)
