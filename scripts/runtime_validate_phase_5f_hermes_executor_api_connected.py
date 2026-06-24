import requests
import sys

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

print("Running Runtime Validations for Phase 5F: Hermes Executor API Connected...")

test("GET /tokyo/ui/status", "GET", f"{BASE_URL}/tokyo/system/health", 200)

lab_status = test("GET /tokyo/plugins/hermes/lab/status", "GET", f"{BASE_URL}/tokyo/plugins/hermes/lab/status", 200)

exec_status = test("GET /tokyo/plugins/hermes/executor/status", "GET", f"{BASE_URL}/tokyo/plugins/hermes/executor/status", 200)
if exec_status:
    data = exec_status.json()
    if data.get("connected"):
        print("[PASS] executor connected is True")
    else:
        print("[FAIL] executor connected is False")
        
    mode = data.get("mode")
    if mode in ["real_hermes_api", "hermes_shim"]:
        print(f"[PASS] executor mode is {mode}")
    else:
        print(f"[FAIL] executor mode is {mode} (expected real_hermes_api or hermes_shim)")
        
    auth_masked = data.get("auth_masked", "")
    if auth_masked.startswith("Bearer tkos_****") or auth_masked == "Bearer pending":
        print("[PASS] Token properly masked")
    else:
        print("[FAIL] Token not properly masked")

# Test job execution
execute_res = test("POST /tokyo/plugins/hermes/executor/execute (hermes_executor_ok)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/executor/execute", 200, {
    "command": "Use o Ollama/Qwen para responder apenas HERMES_EXECUTOR_OK",
    "mode": "lab_unlocked"
})
if execute_res:
    data = execute_res.json()
    if data.get("ok"):
        print("[PASS] executor execute succeeded")
        job_id = data.get("data", {}).get("job_id") or data.get("job_id")
        
        if job_id:
            # Check jobs list
            jobs_res = test("GET /tokyo/plugins/hermes/executor/jobs", "GET", f"{BASE_URL}/tokyo/plugins/hermes/executor/jobs", 200)
            if jobs_res:
                jobs_data = jobs_res.json()
                found = any(j.get("job_id") == job_id for j in jobs_data.get("jobs", []))
                if found:
                    print("[PASS] Job correctly registered in jobs list")
                else:
                    print("[FAIL] Job NOT found in jobs list")
        else:
            print("[FAIL] No job_id returned")
    else:
        print(f"[FAIL] executor execute failed: {data}")

# Test lab execution routes through shim
lab_exec1 = test("POST /tokyo/plugins/hermes/lab/execute (Abra example.com)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {
    "command": "Abra https://example.com",
    "mode": "lab_unlocked"
})
if lab_exec1:
    data = lab_exec1.json()
    if data.get("ok") and data.get("summary") and "Example Domain" in data.get("summary"):
        print("[PASS] Lab execute browser through shim succeeded")
    else:
        print(f"[FAIL] Lab execute browser failed: {data}")

lab_exec2 = test("POST /tokyo/plugins/hermes/lab/execute (Crie um arquivo)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {
    "command": "Crie um arquivo hermes_executor_ok.md no workspace",
    "mode": "lab_unlocked"
})
if lab_exec2:
    data = lab_exec2.json()
    if data.get("ok"):
        print("[PASS] Lab execute file creation through shim succeeded")
    else:
        print(f"[FAIL] Lab execute file creation failed: {data}")

lab_exec3 = test("POST /tokyo/plugins/hermes/lab/execute (Blocked rm -rf)", "POST", f"{BASE_URL}/tokyo/plugins/hermes/lab/execute", 200, {
    "command": "rm -rf /DATA/AppData/tokyoos_src",
    "mode": "lab_unlocked"
})
if lab_exec3:
    data = lab_exec3.json()
    if data.get("status") == "blocked":
        print("[PASS] Critical blocked command correctly intercepted before shim")
    else:
        print("[FAIL] Critical blocked command bypassed safety gate!")

print("Validations Complete.")
