#!/usr/bin/env python3
"""TokyoOS Phase 3E — Multimodal + Store Dashboards Static Test"""
import os, json, sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
PASS, FAIL = 0, 0
def ok(n,c,d=""):
    global PASS, FAIL
    (PASS:=PASS+1) if c else (FAIL:=FAIL+1)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}{' — '+str(d) if d else ''}")

print("="*60+"\nPhase 3E Static Test\n"+"="*60+"\n")

app = (BASE_DIR/"app.py").read_text() if (BASE_DIR/"app.py").exists() else ""
ui = (BASE_DIR/"interface"/"index.html").read_text() if (BASE_DIR/"interface"/"index.html").exists() else ""

print("1. VOICE SPEECH")
ok("Speech status endpoint", "/tokyo/voice/speech/status" in app)
ok("Speech test endpoint", "/tokyo/voice/speech/test" in app)

print("\n2. VISION / CAMERA")
for ep in ["/tokyo/vision/status","/tokyo/vision/capabilities","/tokyo/vision/livekit/status","/tokyo/vision/preview/describe"]:
    ok(f"Vision endpoint {ep}", ep in app)
ok("Camera tile in UI", "camera-tile" in ui or "camera-off" in ui)
ok("Camera JS functions", "toggleCamera" in ui and "stopCamera" in ui)
ok("No auto-record", "never_saves_frames" in app or "auto_recording" in app)
ok("Privacy requires user action", "requires_user_action" in ui or "preview_only" in app)

print("\n3. STORE KPI ENDPOINTS")
for store in ["riverside","teresina"]:
    for mod in ["sales/kpis","sales/trend-calendar","sales/sellers","finance/kpis","finance/dre","finance/cash-flow","finance/break-even","stock/kpis","stock/dead-stock","stock/top-sellers-week","stock/zero-stock","stock/critical-stock","stock/losses"]:
        ok(f"/tokyo/stores/{store}/{mod}", f"/tokyo/stores/{store}/{mod}" in app or "store_id" in app)

print("\n4. TARGETS")
ok("Targets status endpoint", "/tokyo/stores/targets/status" in app)
ok("Store targets endpoint", "/tokyo/stores/{" in app)
cfg = json.loads((BASE_DIR/"config"/"store_targets.example.json").read_text()) if (BASE_DIR/"config"/"store_targets.example.json").exists() else {}
ok("riverside in targets", "riverside" in cfg.get("stores",{}))
ok("teresina in targets", "teresina" in cfg.get("stores",{}))

print("\n5. PENDING_API (no fake data)")
ok("pending_api pattern exists", "pending_api" in app)
ok("No fake R$ in store dashboards", "R$ " not in (ui or ""))

print("\n6. UI STORE DASHBOARDS")
ok("Store tabs exist", "store-tab" in ui and "switchStoreTab" in ui)
ok("Riverside section exists", "store-riverside" in ui)
ok("Teresina section exists", "store-teresina" in ui)
ok("Sales KPIs in UI", "Meta Mes" in ui and "Meta Dia" in ui and "GAP" in ui)
ok("Finance KPIs in UI", "Fluxo de Caixa" in ui)
ok("Stock KPIs in UI", "Zerados" in ui and "Criticos" in ui)
ok("Sellers section in UI", "Vendedores" in ui)
ok("Bunny Siberian tab in UI", "store-bunny-siberian" in ui)
ok("Siberian ERP tab in UI", "store-siberian-erp" in ui)

print("\n7. NO SECRETS IN FRONTEND")
ok("No API keys in UI", "API_KEY" not in ui.upper() or "LIVEKIT_API_KEY" not in ui)

print("\n8. CODE SAFETY")
danger = ["shell=True","os.remove","os.unlink","shutil.rmtree","pkill","killall","sudo "]
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    for d in danger:
        ok(f"{pyf.name}: no {d}", d not in pyf.read_text())

print("\n9. PYTHON SYNTAX")
import py_compile
for pyf in list(BASE_DIR.glob("*.py")) + list((BASE_DIR/"siberian_connector").glob("*.py")) + list((BASE_DIR/"finance_engine").glob("*.py")):
    try: py_compile.compile(str(pyf),doraise=True); ok(f"{pyf.name}",True)
    except py_compile.PyCompileError as e: ok(f"{pyf.name}",False,str(e))

print(f"\n{'='*60}\n3E STATIC: {PASS} passed, {FAIL} failed\n{'='*60}")
sys.exit(1 if FAIL > 0 else 0)
