import requests
import sys
import time

def validate_zimaos_deploy():
    ZIMA_IP = "192.168.1.173"
    ZIMA_PORT = "8788"
    BASE_URL = f"http://{ZIMA_IP}:{ZIMA_PORT}"
    
    print(f"Starting Phase 15 ZimaOS True Fusion Deployment Validation on {BASE_URL}...")
    
    # Wait for service to be up
    max_retries = 10
    service_up = False
    for i in range(max_retries):
        try:
            r = requests.get(f"{BASE_URL}/ui", timeout=5)
            if r.status_code == 200:
                service_up = True
                break
        except Exception:
            print(f"Waiting for TokyoOS to start... ({i+1}/{max_retries})")
            time.sleep(5)
            
    if not service_up:
        print("[FAIL] ZimaOS service did not come online.")
        sys.exit(1)
        
    print("[PASS] ZimaOS service is online and responding at /ui.")
    
    # 1. Test /tokyo/doctor
    try:
        r = requests.get(f"{BASE_URL}/tokyo/doctor", timeout=5)
        assert r.status_code == 200
        print("[PASS] /tokyo/doctor responded correctly.")
    except Exception as e:
        print(f"[FAIL] /tokyo/doctor failed: {e}")
        sys.exit(1)
        
    # 2. Test Agent Core Status via Bridge
    try:
        r = requests.get(f"{BASE_URL}/tokyo/agent-core/status", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["origin"] == "openjarvis_core"
        print("[PASS] /tokyo/agent-core/status (Bridge) responded correctly.")
    except Exception as e:
        print(f"[FAIL] /tokyo/agent-core/status failed: {e}")
        sys.exit(1)
        
    # 3. Test Zero Mock Gate
    try:
        payload = {"agent_name": "tokyo_cfo", "action": "get_dre"}
        r = requests.post(f"{BASE_URL}/tokyo/bunny-agents/invoke", json=payload, timeout=5)
        assert r.status_code == 200
        data = r.json()
        if "SIBERIAN_NOT_CONFIGURED" in data["data_status"]:
            print("[PASS] Zero Mock Gate active - Siberian not configured in ZimaOS.")
        elif "SAFE_READ_ONLY" in data["data_status"]:
            print("[PASS] Zero Mock Gate active - Siberian connected securely.")
        else:
            raise Exception("Invalid Zero Mock Gate response.")
    except Exception as e:
        print(f"[FAIL] Zero Mock Gate test failed: {e}")
        sys.exit(1)
        
    # 4. Test SafetyGate
    try:
        payload = {"agent_name": "general", "action": "sudo rm -rf /"}
        r = requests.post(f"{BASE_URL}/tokyo/operator/execute", json=payload, timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["data_status"] == "blocked"
        print("[PASS] SafetyGate successfully blocked malicious command.")
    except Exception as e:
        print(f"[FAIL] SafetyGate test failed: {e}")
        sys.exit(1)

    print("\n[SUCCESS] Phase 15 True Fusion deployed and validated successfully on ZimaOS.")

if __name__ == "__main__":
    validate_zimaos_deploy()
