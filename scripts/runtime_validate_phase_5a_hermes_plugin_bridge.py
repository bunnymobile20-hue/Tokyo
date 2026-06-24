import requests
import sys

BASE_URL = "http://127.0.0.1:8788"

def run_tests():
    print("Running Runtime Validations for Phase 5A Hermes Plugin Bridge...")

    try:
        # 1. Test Status
        res = requests.get(f"{BASE_URL}/tokyo/plugins/hermes/status")
        if res.status_code == 200:
            print("[PASS] GET /tokyo/plugins/hermes/status")
        else:
            print(f"[FAIL] GET /tokyo/plugins/hermes/status returned {res.status_code}")

        # 2. Test Capabilities
        res = requests.get(f"{BASE_URL}/tokyo/plugins/hermes/capabilities")
        if res.status_code == 200:
            print("[PASS] GET /tokyo/plugins/hermes/capabilities")
        else:
            print(f"[FAIL] GET /tokyo/plugins/hermes/capabilities returned {res.status_code}")

        # 3. Test Ollama
        res = requests.get(f"{BASE_URL}/tokyo/plugins/hermes/ollama/status")
        if res.status_code == 200:
            print("[PASS] GET /tokyo/plugins/hermes/ollama/status")
        else:
            print(f"[FAIL] GET /tokyo/plugins/hermes/ollama/status returned {res.status_code}")

        # 4. Test Dry-Run Safe
        res = requests.post(f"{BASE_URL}/tokyo/plugins/hermes/dry-run", json={
            "request_id": "test-123",
            "command": "check status"
        })
        if res.status_code == 200 and res.json().get("risk") == "low":
            print("[PASS] POST /tokyo/plugins/hermes/dry-run (low risk)")
        else:
            print(f"[FAIL] POST /tokyo/plugins/hermes/dry-run (low risk): {res.json()}")

        # 5. Test Dry-Run Critical
        res = requests.post(f"{BASE_URL}/tokyo/plugins/hermes/dry-run", json={
            "request_id": "test-124",
            "command": "rm -rf /"
        })
        if res.status_code == 200 and res.json().get("status") == "blocked":
            print("[PASS] POST /tokyo/plugins/hermes/dry-run (critical blocked)")
        else:
            print(f"[FAIL] POST /tokyo/plugins/hermes/dry-run (critical blocked): {res.json()}")

        # 6. Test UI is alive
        res = requests.get(f"{BASE_URL}/ui")
        if res.status_code == 200:
            print("[PASS] GET /ui")
        else:
            print(f"[FAIL] GET /ui returned {res.status_code}")

    except Exception as e:
        print(f"[ERROR] Could not run tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
