import requests
import sys

def run_tests():
    BASE_URL = "http://192.168.1.173:8788"
    
    print("==================================================")
    print("PHASE 17: SIBERIAN READ-ONLY CONNECTOR (ZIMAOS)")
    print("==================================================")
    
    routes = [
        "/tokyo/siberian/status",
        "/tokyo/siberian/health",
        "/tokyo/siberian/discovery",
        "/tokyo/siberian/companies",
        "/tokyo/siberian/stores",
        "/tokyo/siberian/products",
        "/tokyo/siberian/sales",
        "/tokyo/siberian/stock",
        "/tokyo/siberian/finance",
        "/tokyo/siberian/reports"
    ]
    
    for route in routes:
        try:
            r = requests.get(f"{BASE_URL}{route}", timeout=5)
            assert r.status_code == 200, f"Route {route} failed: HTTP {r.status_code}"
            data = r.json()
            assert "data_status" in data
            assert data["mode"] == "read_only"
            assert data["write_enabled"] is False
            print(f"[PASS] GET {route} -> {data['data_status']}")
        except Exception as e:
            print(f"[FAIL] Route {route} falhou: {e}")
            sys.exit(1)
            
    # Check UI & Doctor as well
    try:
        r = requests.get(f"{BASE_URL}/tokyo/doctor", timeout=5)
        assert r.status_code == 200
        print("[PASS] /tokyo/doctor está online.")
        
        r2 = requests.get(f"{BASE_URL}/tokyo/agent-core/status", timeout=5)
        assert r2.status_code == 200
        print("[PASS] /tokyo/agent-core/status está online.")
        
        r3 = requests.get(f"{BASE_URL}/ui", timeout=5)
        assert r3.status_code == 200
        print("[PASS] /ui está online.")
    except Exception as e:
        print(f"[FAIL] Verificação extra falhou: {e}")
        sys.exit(1)
        
    print("\n[SUCCESS] Phase 17 Siberian Read-Only Connector validadas no servidor real.")

if __name__ == "__main__":
    run_tests()
