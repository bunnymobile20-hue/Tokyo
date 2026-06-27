from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = TestClient(app)

def test_safety_gate():
    print("Testing SafetyGate...")
    
    payload = {"agent_name": "general", "action": "sudo rm -rf /"}
    resp = client.post("/tokyo/operator/execute", json=payload)
    data = resp.json()
    
    assert resp.status_code == 200
    assert data["origin"] == "native_tokyo"
    assert data["data_status"] == "blocked"
    assert "blocked" in data["message"].lower()
    print("[PASS] SafetyGate successfully blocked malicious command (rm -rf).")

    payload2 = {"agent_name": "general", "action": "cat /etc/passwd"}
    resp2 = client.post("/tokyo/operator/execute", json=payload2)
    data2 = resp2.json()
    assert data2["data_status"] == "blocked"
    print("[PASS] SafetyGate successfully blocked sensitive file read (/etc/passwd).")

if __name__ == "__main__":
    test_safety_gate()
