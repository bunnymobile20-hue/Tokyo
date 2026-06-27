import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from siberian_connector.config import settings

client = TestClient(app)

def test_finance_endpoints():
    print("Testing Finance Endpoints Requires Real Data...")
    
    endpoints = [
        "/tokyo/dashboard/finance/summary",
        "/tokyo/dashboard/finance/dre"
    ]
    
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200
        data = resp.json()
        assert data["safe_to_display"] is False
        if not settings.is_configured:
            assert data["data_status"] == "SIBERIAN_NOT_CONFIGURED"
            
    print("[PASS] Finance Endpoints blocked without real data.")

if __name__ == "__main__":
    test_finance_endpoints()
