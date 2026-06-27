from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = TestClient(app)

def test_zero_mock_gate():
    print("Testing Zero Mock Gate...")
    
    payload = {"agent_name": "tokyo_cfo", "action": "get_dre"}
    resp = client.post("/tokyo/bunny-agents/invoke", json=payload)
    data = resp.json()
    
    assert resp.status_code == 200
    assert data["origin"] == "bridged"
    assert data["data_status"] == "SIBERIAN_NOT_CONFIGURED"
    assert "MOCK DATA ACTIVE" in data["message"]
    print("[PASS] Zero Mock Gate correctly intercepted the CFO agent.")

if __name__ == "__main__":
    test_zero_mock_gate()
