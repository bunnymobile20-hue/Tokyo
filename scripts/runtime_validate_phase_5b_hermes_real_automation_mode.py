import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8788"

def run_tests():
    print("Running Runtime Validations for Phase 5B Hermes Real Automation Mode...")

    try:
        # 1. Test UI Status
        res = requests.get(f"{BASE_URL}/tokyo/ui/status")
        if res.status_code == 200:
            print("[PASS] GET /tokyo/ui/status")
        else:
            print(f"[FAIL] GET /tokyo/ui/status returned {res.status_code}")

        # 2. Test Hermes Status
        res = requests.get(f"{BASE_URL}/tokyo/plugins/hermes/status")
        if res.status_code == 200:
            status_data = res.json()
            if status_data.get("automation_mode") == "active_assisted":
                print("[PASS] GET /tokyo/plugins/hermes/status (mode is active_assisted)")
            else:
                print(f"[FAIL] GET /tokyo/plugins/hermes/status mode is {status_data.get('automation_mode')}")
        else:
            print(f"[FAIL] GET /tokyo/plugins/hermes/status returned {res.status_code}")

        # 3. Test Ollama Status
        res = requests.get(f"{BASE_URL}/tokyo/plugins/hermes/ollama/status")
        if res.status_code == 200:
            print("[PASS] GET /tokyo/plugins/hermes/ollama/status")
        else:
            print(f"[FAIL] GET /tokyo/plugins/hermes/ollama/status returned {res.status_code}")

        # 4. Test Low-Risk Execution (Ollama chat)
        res = requests.post(f"{BASE_URL}/tokyo/plugins/hermes/execute", json={
            "command": "resumo sobre tokyoos",
            "mode": "active_assisted",
            "model": "qwen2.5:32b"
        })
        data = res.json()
        if res.status_code == 200 and data.get("ok") and data.get("status") == "completed":
            print("[PASS] POST /tokyo/plugins/hermes/execute (low risk - ollama chat)")
        else:
            print(f"[FAIL] POST /tokyo/plugins/hermes/execute (low risk - ollama chat): {data}")

        # 5. Test Low-Risk Execution (Workspace note)
        res = requests.post(f"{BASE_URL}/tokyo/plugins/hermes/execute", json={
            "command": "crie uma nota de teste",
            "mode": "active_assisted"
        })
        data = res.json()
        if res.status_code == 200 and data.get("ok") and data.get("status") == "completed":
            print("[PASS] POST /tokyo/plugins/hermes/execute (low risk - workspace note)")
        else:
            print(f"[FAIL] POST /tokyo/plugins/hermes/execute (low risk - workspace note): {data}")

        # 6. Test Critical Blocked
        res = requests.post(f"{BASE_URL}/tokyo/plugins/hermes/execute", json={
            "command": "rm -rf /",
            "mode": "active_assisted"
        })
        data = res.json()
        if res.status_code == 200 and data.get("status") == "blocked":
            print("[PASS] POST /tokyo/plugins/hermes/execute (critical blocked)")
        else:
            print(f"[FAIL] POST /tokyo/plugins/hermes/execute (critical blocked): {data}")

        # 7. Test Medium Risk Pending
        res = requests.post(f"{BASE_URL}/tokyo/plugins/hermes/execute", json={
            "command": "open browser to tokyoos",
            "mode": "active_assisted"
        })
        data = res.json()
        if res.status_code == 200 and data.get("status") == "pending_confirmation":
            print("[PASS] POST /tokyo/plugins/hermes/execute (medium risk pending)")
            job_id = data.get("job_id")
            
            # Confirm it
            confirm_res = requests.post(f"{BASE_URL}/tokyo/plugins/hermes/confirm", json={
                "pending_id": job_id,
                "confirm": True
            })
            if confirm_res.status_code == 200:
                print("[PASS] POST /tokyo/plugins/hermes/confirm (confirmed)")
            else:
                print(f"[FAIL] POST /tokyo/plugins/hermes/confirm failed")
        else:
            print(f"[FAIL] POST /tokyo/plugins/hermes/execute (medium risk pending): {data}")

        # 8. Test Audit logs
        res = requests.get(f"{BASE_URL}/tokyo/plugins/hermes/audit")
        if res.status_code == 200:
            print("[PASS] GET /tokyo/plugins/hermes/audit")
        else:
            print(f"[FAIL] GET /tokyo/plugins/hermes/audit returned {res.status_code}")

    except Exception as e:
        print(f"[ERROR] Could not run tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
