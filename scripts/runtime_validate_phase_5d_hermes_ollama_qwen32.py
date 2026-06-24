import requests
import sys
import time

BASE_URL = "http://192.168.1.173:8788"

print("Running Runtime Validations for Phase 5D: Hermes Ollama Qwen32 Lab Unlocked...")

def test(name, req_method, url, expected_status=None, json_data=None):
    try:
        res = requests.request(req_method, url, json=json_data, timeout=90)
        if expected_status and res.status_code != expected_status:
            print(f"[FAIL] {name}: Expected status {expected_status}, got {res.status_code}")
            return None
        print(f"[PASS] {name}")
        return res.json() if res.text else None
    except Exception as e:
        print(f"[FAIL] {name}: Request error - {e}")
        return None

# 1. UI Status
test("GET /tokyo/ui/status", "GET", f"{BASE_URL}/tokyo/ui/status", 200)

# 2. Lab Status
lab_status = test("GET /tokyo/plugins/hermes/lab/status", "GET", f"{BASE_URL}/tokyo/plugins/hermes/lab/status", 200)
if lab_status:
    if lab_status.get("operation_mode") != "lab_unlocked":
        print(f"[FAIL] Operation mode is {lab_status.get('operation_mode')} instead of lab_unlocked")
    else:
        print(f"[PASS] operation_mode is lab_unlocked")
    
    if lab_status.get("demo_only") is not False:
        print(f"[FAIL] demo_only should be False")
    else:
        print(f"[PASS] demo_only is False")

    if lab_status.get("provider") != "ollama":
        print(f"[FAIL] provider is not ollama")
    else:
        print(f"[PASS] provider is ollama")

# 3. Lab Models
lab_models = test("GET /tokyo/plugins/hermes/lab/models", "GET", f"{BASE_URL}/tokyo/plugins/hermes/lab/models", 200)

# 4. Test Ollama Command
res_ollama = test("POST /tokyo/plugins/hermes/lab/test-ollama", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/test-ollama", 200)
if res_ollama:
    if "QWEN32_OK" in res_ollama.get("summary", ""):
        print("[PASS] test-ollama returned QWEN32_OK")
    else:
        print(f"[FAIL] test-ollama did not return QWEN32_OK. Response: {res_ollama}")

# 5. Execute Command - Document creation
res_doc = test("POST /tokyo/plugins/hermes/lab/execute (Document)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {"command": "Crie um documento teste_qwen32.md no workspace", "mode": "lab_unlocked"})
if res_doc and res_doc.get("ok"):
    print("[PASS] Document creation succeeded")
else:
    print(f"[FAIL] Document creation failed: {res_doc}")

# 6. Execute Command - Spreadsheet creation
res_sheet = test("POST /tokyo/plugins/hermes/lab/execute (Spreadsheet)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {"command": "Crie uma planilha teste_qwen32.csv no workspace", "mode": "lab_unlocked"})
if res_sheet and res_sheet.get("ok"):
    print("[PASS] Spreadsheet creation succeeded")
else:
    print(f"[FAIL] Spreadsheet creation failed: {res_sheet}")

# 7. Execute Command - Browser missing dependency
res_browser = test("POST /tokyo/plugins/hermes/lab/execute (Browser)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {"command": "Abra https://example.com e leia o título", "mode": "lab_unlocked"})
if res_browser and res_browser.get("status") == "capability_missing":
    print("[PASS] Browser returned capability_missing")
else:
    print(f"[FAIL] Browser did not return capability_missing: {res_browser}")

# 8. Execute Command - Critical protection
res_critical = test("POST /tokyo/plugins/hermes/lab/execute (Critical Protection)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {"command": "rm -rf /DATA/AppData/tokyoos_src", "mode": "lab_unlocked"})
if res_critical and res_critical.get("status") == "blocked":
    print("[PASS] Critical command was properly blocked")
else:
    print(f"[FAIL] Critical command was NOT blocked: {res_critical}")

print("Validations Complete.")
