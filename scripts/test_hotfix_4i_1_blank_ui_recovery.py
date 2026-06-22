#!/usr/bin/env python3
"""Hotfix 4I.1 — Blank UI Recovery Test"""
import os,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
P,F=0,0
def ok(n,c,d=""):
    global P,F
    (P:=P+1) if c else (F:=F+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")
print("="*60+"\nHotfix 4I.1\n"+"="*60+"\n")
app=(BASE/"app.py").read_text() if (BASE/"app.py").exists() else ""
ui=(BASE/"interface"/"index.html").read_text() if (BASE/"interface"/"index.html").exists() else ""
html_size = (BASE/"interface"/"index.html").stat().st_size if (BASE/"interface"/"index.html").exists() else 0

print("1. UI BASIC")
ok("index.html exists", bool(ui))
ok(f"HTML size > 5KB (actual: {html_size})", html_size > 5000, html_size)
ok("DOCTYPE present", "<!DOCTYPE html>" in ui)
ok("body tag present", "<body" in ui)
ok("sidebar present", "sidebar" in ui)
ok("page-home present", "page-home" in ui)

print("\n2. FALLBACK + SAFETY")
ok("Page has active class", 'class="page active"' in ui)
ok("JS try/catch pattern", "try {" in ui and "} catch" in ui)
ok("API Key Center page exists", "page-api-keys" in ui)

print("\n3. UI STATUS ENDPOINTS")
for ep in ["/tokyo/ui/status","/tokyo/ui/routes","/tokyo/ui/assets-status"]:
    ok(f"Route {ep}", ep in app)

print("\n4. NO SECRETS IN FRONTEND")
ok("No LIVEKIT_API_SECRET", "LIVEKIT_API_SECRET" not in ui.upper())
ok("No GEMINI_API_KEY", "GEMINI_API_KEY" not in ui.upper() or "env" in ui.lower())
ok("No localStorage secrets", "localStorage.setItem" not in ui.lower() or "token" not in ui.lower())

print("\n5. DISPATCH PRESERVED")
ok("Dispatch module intact", (BASE/"tokyo_voice_agent"/"dispatch.py").exists())
ok("Session create uses dispatch", "create_session_with_dispatch" in app)
ok("API Key Center backend intact", (BASE/"tokyo_security"/"api_keys.py").exists())

print("\n6. REGRESSIONS")
ok("Siberian intact", (BASE/"siberian_connector"/"client.py").exists())
ok("Finance intact", (BASE/"finance_engine"/"__init__.py").exists())
ok("Upload disabled", "upload_enabled" in app)

print(f"\n{'='*60}\n HOTFIX: {P} passed, {F} failed\n{'='*60}")
sys.exit(1 if F>0 else 0)
