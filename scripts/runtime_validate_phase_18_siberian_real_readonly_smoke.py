import requests
import sys

def run_tests():
    BASE_URL = "http://192.168.1.173:8788"
    
    print("==================================================")
    print("PHASE 18: SIBERIAN REAL HANDSHAKE SMOKE TEST (ZIMAOS)")
    print("==================================================")
    
    endpoints = [
        "/ui",
        "/tokyo/siberian/status",
        "/tokyo/siberian/health",
        "/tokyo/siberian/discovery",
        "/tokyo/siberian/companies",
        "/tokyo/siberian/stores",
        "/tokyo/siberian/products",
        "/tokyo/siberian/sales",
        "/tokyo/siberian/stock",
        "/tokyo/siberian/finance",
        "/tokyo/siberian/reports",
        "/tokyo/doctor",
        "/tokyo/agent-core/status"
    ]
    
    for ep in endpoints:
        try:
            r = requests.get(f"{BASE_URL}{ep}", timeout=5)
            assert r.status_code == 200, f"Endpoint {ep} HTTP {r.status_code}"
            
            # Checks based on the prompt criteria
            if "siberian" in ep and ep not in ["/tokyo/siberian/health", "/tokyo/siberian/status"]:
                data = r.json()
                assert "data_status" in data
                # Since we haven't configured it yet (the user will do it manually later),
                # it should safely return SIBERIAN_NOT_CONFIGURED.
                # If they already configured it, it should return real_data or similar.
                status = data.get("data_status")
                print(f"[PASS] GET {ep} -> {status}")
            else:
                print(f"[PASS] GET {ep} -> Online")
                
        except Exception as e:
            print(f"[FAIL] Endpoint {ep} falhou: {e}")
            sys.exit(1)
            
    print("\n[SUCCESS] Runtime Phase 18 Smoke Test concluído!")

if __name__ == "__main__":
    run_tests()
