from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = TestClient(app)

def test_ui_endpoints():
    print("Testing UI Endpoints...")
    
    resp = client.get("/ui")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["Content-Type"]
    print("[PASS] /ui endpoint returns HTML.")

    resp2 = client.get("/tokyo/doctor")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert "checks" in data2
    print("[PASS] /tokyo/doctor endpoint returns diagnostic JSON.")

if __name__ == "__main__":
    test_ui_endpoints()
