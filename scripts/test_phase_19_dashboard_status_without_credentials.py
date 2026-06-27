import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from siberian_connector.config import settings

client = TestClient(app)

def test_dashboard_status():
    print("Testing Dashboard Status Without Credentials...")
    
    endpoints = [
        "/tokyo/dashboard/finance/status",
        "/tokyo/dashboard/stock/status",
        "/tokyo/dashboard/executive/status"
    ]
    
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200
        data = resp.json()
        assert data["safe_to_display"] is False
        if not settings.is_configured:
            assert data["data_status"] == "SIBERIAN_NOT_CONFIGURED"
            
    print("[PASS] Dashboards return SIBERIAN_NOT_CONFIGURED securely.")

if __name__ == "__main__":
    test_dashboard_status()
