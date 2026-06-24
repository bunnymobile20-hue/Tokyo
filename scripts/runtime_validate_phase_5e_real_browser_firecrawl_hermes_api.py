import requests
import sys
import time

BASE_URL = "http://192.168.1.173:8788"

def test(name, req_method, url, expected_status=None, json_data=None):
    try:
        res = requests.request(req_method, url, json=json_data, timeout=90)
        if expected_status and res.status_code != expected_status:
            print(f"[FAIL] {name}: Expected status {expected_status}, got {res.status_code}")
            return None
        print(f"[PASS] {name}")
        return res
    except Exception as e:
        print(f"[FAIL] {name}: Request error - {e}")
        return None

print("Running Runtime Validations for Phase 5E: Browser, Firecrawl, Hermes API...")

test("GET /tokyo/ui/status", "GET", f"{BASE_URL}/tokyo/system/health", 200)

lab_status = test("GET /tokyo/plugins/hermes/lab/status", "GET", f"{BASE_URL}/tokyo/plugins/hermes/lab/status", 200)
if lab_status:
    data = lab_status.json()
    if data.get("operation_mode") == "lab_unlocked":
        print("[PASS] operation_mode is lab_unlocked")
    else:
        print(f"[FAIL] operation_mode is {data.get('operation_mode')}")

    if data.get("browser_provider") != "missing_dependency":
        print(f"[PASS] browser_provider is {data.get('browser_provider')}")
    else:
        print(f"[WARN] browser_provider is missing_dependency")
        
    if not data.get("demo_only"):
        print("[PASS] demo_only is False")
    else:
        print("[FAIL] demo_only is True")

test("GET /tokyo/plugins/hermes/browser/status", "GET", f"{BASE_URL}/tokyo/plugins/hermes/browser/status", 200)

open_url_res = test("POST /tokyo/plugins/hermes/browser/open-url", "POST", f"{BASE_URL}/tokyo/plugins/hermes/browser/open-url", 200, {"url": "https://example.com"})
if open_url_res:
    data = open_url_res.json()
    if data.get("ok"):
        print("[PASS] open-url example.com succeeded")
    else:
        print(f"[FAIL] open-url example.com failed: {data.get('error')}")

test("GET /tokyo/plugins/hermes/firecrawl/status", "GET", f"{BASE_URL}/tokyo/plugins/hermes/firecrawl/status", 200)
test("GET /tokyo/plugins/hermes/executor/status", "GET", f"{BASE_URL}/tokyo/plugins/hermes/executor/status", 200)

# Test real execute commands
execute_browser = test("POST /tokyo/plugins/hermes/lab/execute (Abra https://example.com)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {
    "command": "Abra https://example.com e leia o título",
    "mode": "lab_unlocked"
})
if execute_browser:
    data = execute_browser.json()
    if data.get("ok"):
        print("[PASS] Lab execute browser succeeded")
    else:
        print(f"[FAIL] Lab execute browser failed: {data}")

execute_blocked = test("POST /tokyo/plugins/hermes/lab/execute (Critical Protection)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {
    "command": "rm -rf /DATA/AppData/tokyoos_src",
    "mode": "lab_unlocked"
})
if execute_blocked:
    data = execute_blocked.json()
    if data.get("status") == "blocked":
        print("[PASS] Critical command was properly blocked")
    else:
        print("[FAIL] Critical command was not blocked")

print("Validations Complete.")
