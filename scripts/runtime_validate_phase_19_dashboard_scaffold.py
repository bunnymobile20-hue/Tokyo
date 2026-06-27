import requests
import sys

def run_tests():
    BASE_URL = "http://192.168.1.173:8788"
    
    print("==================================================")
    print("PHASE 19: DASHBOARD SCAFFOLD REAL DATA GATE (ZIMAOS)")
    print("==================================================")
    
    endpoints = [
        "/tokyo/dashboard/finance/status",
        "/tokyo/dashboard/finance/summary",
        "/tokyo/dashboard/finance/dre",
        "/tokyo/dashboard/stock/status",
        "/tokyo/dashboard/stock/summary",
        "/tokyo/dashboard/executive/status",
        "/tokyo/dashboard/executive/summary"
    ]
    
    for ep in endpoints:
        try:
            r = requests.get(f"{BASE_URL}{ep}", timeout=5)
            assert r.status_code == 200, f"Endpoint {ep} HTTP {r.status_code}"
            data = r.json()
            
            # Garante que as propriedades obrigatórias existam
            assert "data_status" in data
            assert "safe_to_display" in data
            assert "confidence" in data
            assert "warnings" in data
            assert "write_enabled" in data
            assert data["write_enabled"] is False
            
            # Se não há config real no servidor, safe_to_display tem que ser false obrigatoriamente
            if data["data_status"] == "SIBERIAN_NOT_CONFIGURED":
                assert data["safe_to_display"] is False
                
            print(f"[PASS] GET {ep} -> {data['data_status']} | Safe to Display: {data['safe_to_display']}")
                
        except Exception as e:
            print(f"[FAIL] Endpoint {ep} falhou: {e}")
            sys.exit(1)
            
    print("\n[SUCCESS] Runtime Phase 19 Dashboards validados! Scaffolds seguros.")

if __name__ == "__main__":
    run_tests()
