from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = TestClient(app)

def test_fusion_architecture():
    print("Testing Fusion Architecture Bridge...")
    
    resp = client.get("/tokyo/agent-core/status")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["origin"] == "openjarvis_core"
    assert data["data_status"] == "safe_read_only"
    print("[PASS] Agent Core Status bridged correctly.")
    
    resp = client.get("/tokyo/workflows/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["origin"] == "openjarvis_core"
    print("[PASS] Workflows Status bridged correctly.")

if __name__ == "__main__":
    test_fusion_architecture()
