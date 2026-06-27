from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = TestClient(app)

def test_routes():
    print("Testing Siberian Routes...")
    
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
        resp = client.get(route)
        assert resp.status_code == 200, f"Route {route} failed with {resp.status_code}"
        data = resp.json()
        assert "data_status" in data
        assert "origin" in data
        assert data["mode"] == "read_only"
        assert data["write_enabled"] is False
        
    print("[PASS] All GET endpoints return transparent read-only response schemas.")

if __name__ == "__main__":
    test_routes()
